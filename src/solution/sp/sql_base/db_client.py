from fastapi import HTTPException

import config as conf
from bst_core.shared.logger import get_logger
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from core.api.dtos import StatusResponseSchema
from core.spi.db_client import DBClientSPI
from solution.sp.sql_base.models import IngestionRequestStatus, Base

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
            args['ssl_key'] = conf.DB_SSL_PATH_CERT
        return args

    async def _insert(self, row: Base):
        async with self.session() as session:
            session.add(row)
            await session.flush()
            row_id = row.id
            await session.commit()
            return row_id

    async def insert_new_request(self, request_params: dict) -> str:
        """
        Insert new request to the DB and return it ID
        :param request_params: parameters of the request
        :return: id of the DB record
        """

        request = IngestionRequestStatus(**request_params)
        return await self._insert(request)

    async def get_request_status(self, request_id: str) -> dict:
        """
        Get status of request
        :param request_id:
        """
        async with self.session() as session:
            stmt = select(IngestionRequestStatus).where(IngestionRequestStatus.id == request_id)
            query = await session.execute(stmt)
            resp = query.scalars().first()
            if resp is None:
                raise HTTPException(status_code=404, detail=f"Can not fund request by id {request_id}")
        return StatusResponseSchema(tenant_id=resp.tenant_id,
                                    app_id=resp.app_id,
                                    entity_type=resp.entity_type,
                                    src_type=resp.src_type,
                                    is_batch_required=resp.is_batch_required,
                                    batch_size=resp.batch_size,
                                    enrich_oncreation=resp.enrich_oncreation,
                                    status=resp.status,
                                    start_time=resp.start_time,
                                    end_time=resp.end_time,
                                    ).dict(exclude_none=True)
