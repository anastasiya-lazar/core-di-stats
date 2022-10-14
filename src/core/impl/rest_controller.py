import json
from fastapi import Request
from opentelemetry import trace
from opentelemetry.propagate import extract, inject

from core.api.dtos import (IngestionParamsSchema, StatusResponseSchema, IngestProgressDataResponse,
                           CreateIngestionStatusSchema, CreateIngestionStatusResponse, UpdateIngestionStatusSchema,
                           GetIngestionStatusSchema)
from core.api.stats_controller import StatsController
from solution.profile import profile

tracer = trace.get_tracer(__name__)


class RestController(StatsController):

    async def ingest_data(self, payload: IngestionParamsSchema) -> IngestProgressDataResponse:
        """
        Handle incoming requests and ingests data into the DB
        """
        with tracer.start_as_current_span('ingest_data',
                                          attributes={'endpoint': '/ingest_data'}) as root:
            root.set_attribute('request_body', json.dumps(payload.dict()))
            with tracer.start_as_current_span('insert_new_request') as insert:
                request_id = await profile.db_client.insert_new_request(payload)
                insert.set_attribute('request_id', request_id)
                return IngestProgressDataResponse(request_id=request_id)

    async def get_status_by_request_id(self, request_id: str) -> StatusResponseSchema:
        """
        Get status of request by id
        """
        with tracer.start_as_current_span('get_status_by_request_id',
                                          attributes={'endpoint': f'/get-status/{request_id}'}) as root:
            root.set_attribute('request_id', request_id)
            return await profile.db_client.get_request_status(request_id)

    async def create_ingestion_status(self, payload: CreateIngestionStatusSchema) -> CreateIngestionStatusResponse:
        """
        Create ingestion status
        """
        with tracer.start_as_current_span('create_ingestion_status',
                                          attributes={'endpoint': '/create-ingestion-status'}) as root:
            root.set_attribute('request_body', json.dumps(payload.dict()))
            ingestion_id = await profile.db_client.db_create_ingestion_status(payload)
            return CreateIngestionStatusResponse(id=ingestion_id)

    async def update_ingestion_status(self, request_id: str, source_id: str, payload: UpdateIngestionStatusSchema):
        """
        Update ingestion status
        """
        with tracer.start_as_current_span('update_ingestion_status',
                                          attributes={'endpoint': f'/update-ingestion-status/{request_id}/{source_id}'}) as root:
            root.set_attribute('request_body', json.dumps(payload.dict()))
            return await profile.db_client.db_update_ingestion_status(request_id, source_id, payload)

    async def get_ingestion_status(self, request_id: str, source_id: str) -> GetIngestionStatusSchema:
        """
        Get ingestion status
        """
        with tracer.start_as_current_span('get_ingestion_status',
                                          attributes={
                                              'endpoint': f'/get-ingestion-status/{request_id}/{source_id}'}) as root:
            root.set_attribute('request_id', request_id)
            root.set_attribute('source_id', source_id)
            return await profile.db_client.db_get_ingestion_status(request_id, source_id)

