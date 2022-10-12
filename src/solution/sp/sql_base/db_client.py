import ssl

from fastapi import HTTPException

import config as conf
from bst_core.shared.logger import get_logger
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_400_BAD_REQUEST

from core.api.dtos import StatusResponseSchema, IngestionParamsSchema, CreateIngestionStatusSchema
from core.spi.db_client import DBClientSPI
from solution.sp.sql_base.models import IngestionRequestStatus, Base, IngestionStatus

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

