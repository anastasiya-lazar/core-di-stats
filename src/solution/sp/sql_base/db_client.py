import ssl

from fastapi import HTTPException

import config as conf
from bst_core.shared.logger import get_logger
from sqlalchemy import update, case
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.exc import IntegrityError

from core.api.dtos import (StatusResponseSchema, IngestionParamsSchema, CreateIngestionStatusSchema,
                           UpdateIngestionStatusSchema, GetIngestionStatusSchema, FilterParams, SubscriberMessageSchema)
from core.spi.db_client import DBClientSPI, DuplicationException, ForeignKeyException, NotFoundException
from solution.sp.sql_base.models import (IngestionRequestStatus, Base, IngestionStatus, RequestStatusEnum,
                                         IngestionStatusEnum, IngestionRequestFilter, SubscriberIngestionStatus,
                                         SubscriberStatusEnum)

logger = get_logger(__name__)


class DBClientSP(DBClientSPI):
    __instance = None
    engine = None
    session = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, *args, **kwargs):
        super(DBClientSP, self).__init__(*args, **kwargs)
        if self.engine is None:
            logger.info(f"Connecting to DB")
            self.engine: AsyncEngine = create_async_engine(
                conf.REQUEST_DB_CONNECTION_STRING,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=0,
                pool_recycle=60 * 60,
                connect_args=self._get_connect_args()
            )
            self.session: sessionmaker = sessionmaker(self.engine, class_=AsyncSession)

    @staticmethod
    def _get_connect_args():
        args = {}
        if conf.DB_SSL_PATH_CERT:
            args['ssl'] = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, capath=conf.DB_SSL_PATH_CERT)
        return args

    async def _insert(self, row: Base, filters=None, ingestion_status: bool = False):
        try:
            async with self.session() as session:
                session.add(row)
                await session.flush()
                if not ingestion_status:
                    row_id = row.id
                    if filters:
                        session.add_all(
                            [IngestionRequestFilter.from_request_param(FilterParams(**f), row_id) for f in filters]
                        )
                await session.commit()
                if not ingestion_status:
                    return row_id
                return "Ok"
        except IntegrityError as e:
            if "Duplicate entry" in e.orig.args[1]:
                raise DuplicationException(e.orig.args[1])
            elif "Cannot add or update a child row: a foreign key constraint fails" in e.orig.args[1]:
                raise ForeignKeyException(e.orig.args[1])
            raise e

    @staticmethod
    async def _update_with_given_payload(session, table, record_id, payload):
        stmt = update(table).where(table.id == record_id).values(**payload)
        ex = await session.execute(stmt)
        await session.commit()
        if ex.rowcount != 1:
            logger.error(f"Can not update {table.__name__} by id {record_id} with payload {payload}")
            raise NotFoundException(f"Can not found {table.__name__} with id {record_id}")

    async def _update_request_table_to_failed(self, request_id: str):
        """
        Update request table to failed
        :param request_id: id of the request
        """
        async with self.session() as session:
            stmt = update(IngestionRequestStatus).where(IngestionRequestStatus.id == request_id).values(
                {"status": RequestStatusEnum.FAILED.value})
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def _get_ingestion_status_by_request_id_and_source_id(session, request_id: str, source_id: str):
        stmt = select(IngestionStatus).where(IngestionStatus.request_id == request_id,
                                             IngestionStatus.source_id == source_id)
        query = await session.execute(stmt)
        ingestion = query.scalars().first()
        if ingestion is None:
            raise NotFoundException(f"Can not found ingestion status by request_id {request_id} "
                                    f"and source_id {source_id}")
        return ingestion

    @staticmethod
    def _subs_where_condition(payload: SubscriberMessageSchema):
        return (SubscriberIngestionStatus.request_id == payload.request_id,
                SubscriberIngestionStatus.subscriber == payload.subscriber,
                SubscriberIngestionStatus.source_id == payload.source_id,
                SubscriberIngestionStatus.file_uri == payload.file_uri)

    async def db_insert_new_request(self, payload: IngestionParamsSchema) -> str:
        """
        Insert new request to the DB and return it ID
        :param payload: parameters of the request
        :return: id of the DB record
        """
        dict_payload = payload.dict()
        filters = dict_payload.pop('filters', [])
        request_status = IngestionRequestStatus(**dict_payload)

        return await self._insert(request_status, filters)

    async def db_get_request_status(self, request_id: str) -> StatusResponseSchema:
        """
        Get status of request
        :param request_id:
        """
        async with self.session() as session:
            stmt = select(IngestionRequestStatus).options(joinedload(
                IngestionRequestStatus.ingestion_statuses), joinedload(
                IngestionRequestStatus.subscriber_ingestion_statuses
            )).where(IngestionRequestStatus.id == request_id)
            query = await session.execute(stmt)
            resp = query.scalars().first()
            if resp is None:
                raise NotFoundException(f"Can not found request status by id {request_id}")
        return StatusResponseSchema.from_orm(resp)

    async def db_create_ingestion_status(self, payload: CreateIngestionStatusSchema) -> str:
        """
        Create ingestion status
        :param payload:
        """
        request = IngestionStatus(**payload.dict())
        return await self._insert(request, ingestion_status=True)

    async def db_update_ingestion_status(self, request_id: str, source_id: str, payload: UpdateIngestionStatusSchema):
        """
        Update ingestion status
        :param request_id:
        :param source_id:
        :param payload:
        """
        if payload.status == IngestionStatusEnum.FAILED.value:
            await self._update_request_table_to_failed(request_id)

        async with self.session() as session:
            stmt = update(IngestionStatus).where(IngestionStatus.request_id == request_id,
                                                 IngestionStatus.source_id == source_id).values(
                **payload.dict(exclude_unset=True))
            ex = await session.execute(stmt)
            await session.commit()
            if ex.rowcount != 1:
                logger.error(f"Can not update {IngestionStatus.__name__} by request_id {request_id} "
                             f"and source_id {source_id} with payload {payload}")
                raise NotFoundException(f"Can not found {IngestionStatus.__name__} with request id {request_id} "
                                        f"and source_id {source_id}")

    async def db_get_ingestion_status(self, request_id: str, source_id: str) -> GetIngestionStatusSchema:
        """
        Get ingestion status
        :param request_id:
        :param source_id:
        """
        async with self.session() as session:
            ingestion = await self._get_ingestion_status_by_request_id_and_source_id(session, request_id, source_id)
            return GetIngestionStatusSchema.from_orm(ingestion)

    async def db_create_or_update_subscriber_ingestion_status(self, payload: SubscriberMessageSchema):
        """
        Create subscriber ingestion status
        :param payload:
        """
        row = SubscriberIngestionStatus(**payload.dict())

        try:
            return await self._insert(row)

        except DuplicationException as de:
            async with self.session() as session:
                logger.info(f"Subscriber ingestion status already exists and will be updated with payload {payload}"
                            f" duplication exception: {de.message}")

                case_creator_for_totals = lambda kv: (kv[0], case(
                    (getattr(SubscriberIngestionStatus, kv[0]) < kv[1], kv[1]),
                    else_=getattr(SubscriberIngestionStatus, kv[0]))
                ) if "total" in kv[0] else kv

                stmt = update(SubscriberIngestionStatus).where(
                    SubscriberIngestionStatus.request_id == payload.request_id,
                    SubscriberIngestionStatus.subscriber == payload.subscriber,
                    SubscriberIngestionStatus.source_id == payload.source_id,
                    SubscriberIngestionStatus.file_uri == payload.file_uri,
                ).values(**dict(map(case_creator_for_totals, payload.dict(exclude_unset=True).items())))

                ex = await session.execute(stmt)
                await session.commit()

                if ex.rowcount != 1:
                    logger.error(f"\n--------------------------------------------------\n"
                                 f"Can not update {SubscriberIngestionStatus.__name__} with payload {payload}\n"
                                 f"--------------------------------------------------")
                else:
                    logger.info(f"\n--------------------------------------------------\n"
                                f"Updated {SubscriberIngestionStatus.__name__} successfully\n"
                                f"--------------------------------------------------")
                    stmt2 = update(SubscriberIngestionStatus).where(
                        SubscriberIngestionStatus.request_id == payload.request_id,
                        SubscriberIngestionStatus.subscriber == payload.subscriber,
                        SubscriberIngestionStatus.source_id == payload.source_id,
                        SubscriberIngestionStatus.file_uri == payload.file_uri,
                    ).values(
                        {"status": case((
                            SubscriberIngestionStatus.total_record_count ==
                            SubscriberIngestionStatus.total_success_count, SubscriberStatusEnum.COMPLETED.value,
                        ), else_=SubscriberIngestionStatus.status)
                        })
                    await session.execute(stmt2)
                    await session.commit()
                    logger.info(f"-----Updated {SubscriberIngestionStatus.__name__} status successfully-----")

        except ForeignKeyException as fke:
            logger.error(f"\n--------------------------------------------------\n"
                         f"Can not create {SubscriberIngestionStatus.__name__} with payload {payload}, "
                         f"exception info: {fke.message}\n"
                         f"--------------------------------------------------")
