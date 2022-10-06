import json
from fastapi import Request
from opentelemetry import trace
from opentelemetry.propagate import extract, inject

from core.api.dtos import IngestionParamsSchema, StatusResponseSchema, IngestProgressDataResponse
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
                return IngestProgressDataResponse(**{'request_id': request_id})

    async def get_status_by_request_id(self, request_id: str) -> StatusResponseSchema:
        """
        Get status of request by id
        """
        with tracer.start_as_current_span('get_status_by_request_id',
                                          attributes={'endpoint': f'/get-status/{request_id}'}) as root:
            root.set_attribute('request_id', request_id)
            return await profile.db_client.get_request_status(request_id)
