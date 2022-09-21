from fastapi import APIRouter, Depends

from bst_core.shared.logger import get_logger

from core.api.dtos import IngestionParamsSchema, StatusResponseSchema, IngestProgressDataResponse
from core.impl.rest_controller import RestController
from solution.channel.fastapi.auth_controller import AuthTokenApiKey

logger = get_logger(__name__)

auth = AuthTokenApiKey(name="api")

router = APIRouter(dependencies=[Depends(auth)],  prefix='/v1/core-di-stats')
rest_controller = RestController()


@router.post("/ingest-data", status_code=201, response_model=IngestProgressDataResponse, tags=["main"])
async def ingest_stats_data(payload: IngestionParamsSchema):
    """Creates a new record in the database with the provided data. Returns the ID of the created record(request id)."""
    return await rest_controller.ingest_data(payload)


@router.get("/get-status/{request_id}", response_model=StatusResponseSchema, tags=["main"])
async def get_status_of_request(request_id: str):
    """Returns the status of the request with the provided ID."""
    return await rest_controller.get_status_by_request_id(request_id)

