from core.api.dtos import MediatorIngestionSchema, StatusResponseSchema
from core.api.stats_controller import StatsController
from solution.profile import profile


class RestController(StatsController):

    async def ingest_data(self, payload: MediatorIngestionSchema):
        db_params = MediatorIngestionSchema(**payload.dict())
        request_id = await profile.db_client.insert_new_request(db_params)
        return {'request_id': request_id}

    async def get_status_by_request_id(self, request_id: str) -> StatusResponseSchema:
        return await profile.db_client.get_request_status(request_id)
