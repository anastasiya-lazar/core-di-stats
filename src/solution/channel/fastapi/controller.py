from fastapi import APIRouter, Depends

from bst_core.shared.logger import get_logger

from core.api.dtos import MediatorIngestionSchema, StatusResponseSchema, IngestDataResponse
from core.impl.rest_controller import RestController
from solution.channel.fastapi.auth_controller import AuthTokenApiKey

logger = get_logger(__name__)

auth = AuthTokenApiKey(name="api")

router = APIRouter(dependencies=[Depends(auth)],  prefix='/v1/core-di-stats')
rest_controller = RestController()


@router.post("/ingest-data", status_code=201, response_model=IngestDataResponse)
async def ingest_stats_data(payload: MediatorIngestionSchema):
    return await rest_controller.ingest_data(payload)


@router.get("/get-status/{request_id}", response_model=StatusResponseSchema)
async def get_latest_schema_version(request_id: str):
    return await rest_controller.get_status_by_request_id(request_id)

