from fastapi import APIRouter

from bst_core.shared.logger import get_logger

from core.api.dtos import MediatorIngestionSchema, StatusResponseSchema
from core.impl.rest_controller import RestController

logger = get_logger(__name__)

router = APIRouter(prefix='')
rest_controller = RestController()


@router.post("/ingestData", status_code=201)
async def ingest_stats_data(payload: MediatorIngestionSchema):
    return await rest_controller.ingest_data(payload)


@router.get("/get_status/{request_id}", response_model=StatusResponseSchema)
async def get_latest_schema_version(request_id: str):
    return await rest_controller.get_status_by_request_id(request_id)
