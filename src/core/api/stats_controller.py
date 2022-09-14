from abc import ABC, abstractmethod

from core.api.dtos import MediatorIngestionSchema, StatusResponseSchema, IngestDataResponse


class StatsController(ABC):
    """
    Base class for the stats handling
    """
    @abstractmethod
    async def ingest_data(self, payload: MediatorIngestionSchema) -> IngestDataResponse:
        """
        Handle incoming requests from mediator to ingest data into the DB
        :param payload: request body
        :return: request ID
        """

    @abstractmethod
    async def get_status_by_request_id(self, request_id: str) -> StatusResponseSchema:
        """
        Get status of request
        :param request_id:
        :return: StatusResponseSchema
        """
