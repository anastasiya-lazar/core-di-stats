import ssl

from fastapi import HTTPException

import config as conf
from bst_core.shared.logger import get_logger
from sqlalchemy import update, func
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_400_BAD_REQUEST

from core.api.dtos import (StatusResponseSchema, IngestionParamsSchema, CreateIngestionStatusSchema,
                           UpdateIngestionStatusSchema)
from core.spi.db_client import DBClientSPI
from solution.sp.sql_base.models import (IngestionRequestStatus, Base, IngestionStatus, RequestStatusEnum,
                                         IngestionStatusEnum)

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

    async def _insert(self, row: Base):
        try:
            async with self.session() as session:
                session.add(row)
                await session.flush()
                row_id = row.id
                await session.commit()
                return row_id
        except IntegrityError as e:
            if "Duplicate entry" in e.orig.args[1]:
                raise DuplicationException(e.orig.args[1])
            elif "Cannot add or update a child row: a foreign key constraint fails" in e.orig.args[1]:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=e.orig.args[1])
            raise e

    async def _update_with_given_payload(self, table, record_id, payload):
        async with self.session() as session:
            stmt = update(table).where(table.id == record_id).values(**payload)
            ex = await session.execute(stmt)
            await session.commit()
            if ex.rowcount != 1:
                logger.error(f"Can not update {table.__name__} with id {record_id} with payload {payload}")
                raise HTTPException(status_code=404, detail=f"Can not found {table.__name__} by id {record_id}")

    @staticmethod
    async def _update_related_table_to_failed(session, record_id, from_table, to_table,
                                              enum_value, id_field_name):
        """
        Updates status of related table record to failed
        :param session: session
        :param record_id: id of the record
        :param from_table: table with the record
        :param to_table: table with the related record
        """
        srmt = select(from_table).where(from_table.id == record_id)
        query = await session.execute(srmt)
        related_record_id = getattr(query.scalars().first(), id_field_name)
        stmt1 = update(to_table).where(to_table.id == related_record_id).values(
            {"status": enum_value})
        await session.execute(stmt1)
        return related_record_id

    async def insert_new_request(self, payload: IngestionParamsSchema) -> str:
        """
        Insert new request to the DB and return it ID
        :param payload: parameters of the request
        :return: id of the DB record
        """

        request = IngestionRequestStatus(**payload.dict())
        return await self._insert(request)

    async def get_request_status(self, request_id: str) -> StatusResponseSchema:
        """
        Get status of request
        :param request_id:
        """
        async with self.session() as session:
            stmt = select(IngestionRequestStatus).where(IngestionRequestStatus.id == request_id)
            query = await session.execute(stmt)
            resp = query.scalars().first()
            if resp is None:
                raise HTTPException(status_code=404, detail=f"Can not found request by id {request_id}")
        return StatusResponseSchema.from_orm(resp)

    async def db_create_ingestion_status(self, payload: CreateIngestionStatusSchema) -> int:
        """
        Create ingestion status
        :param payload:
        """
        request = IngestionStatus(**payload.dict())
        return await self._insert(request)

    async def db_update_ingestion_status(self, ingestion_id: int, payload: UpdateIngestionStatusSchema):
        """
        Update ingestion status
        :param ingestion_id: ingestion status record id
        :param payload: request body
        """
        if payload.status == IngestionStatusEnum.FAILED.value:
            async with self.session() as session:
                await self._update_related_table_to_failed(session, ingestion_id, IngestionStatus,
                                                           IngestionRequestStatus, RequestStatusEnum.FAILED.value,
                                                           "request_id")
                await session.commit()
        await self._update_with_given_payload(IngestionStatus, ingestion_id, payload.dict(exclude_unset=True))
