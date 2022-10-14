from fastapi import APIRouter, Depends

from bst_core.shared.logger import get_logger

from core.api.dtos import (IngestionParamsSchema, StatusResponseSchema, IngestProgressDataResponse,
                           CreateIngestionStatusSchema, CreateIngestionStatusResponse, UpdateIngestionStatusSchema)
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


@router.post("/create-ingestion-status", response_model=CreateIngestionStatusResponse,
             status_code=201, tags=["ingestion-status"])
async def create_ingestion_status(payload: CreateIngestionStatusSchema):
    """Creates a new record in the database with the provided data. Returns the ID of the created record."""
    return await rest_controller.create_ingestion_status(payload)


@router.patch("/update-ingestion-status/{request_id}/{source_id}", status_code=200, tags=["ingestion-status"])
async def update_ingestion_status(request_id: str, source_id: str, payload: UpdateIngestionStatusSchema):
    """Updates the record by id with the provided data."""
    await rest_controller.update_ingestion_status(request_id, source_id, payload)
    return {"message": "Ingestion status is updated successfully"}
