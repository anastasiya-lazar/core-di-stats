from abc import ABC, abstractmethod

from core.api.dtos import (IngestionParamsSchema, StatusResponseSchema, IngestProgressDataResponse,
                           CreateIngestionStatusSchema, CreateIngestionStatusResponse, UpdateIngestionStatusSchema)


class StatsController(ABC):
    """
    Base class for the stats handling
    """
    @abstractmethod
    async def ingest_data(self, payload: IngestionParamsSchema) -> IngestProgressDataResponse:
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

    @abstractmethod
    async def create_ingestion_status(self, payload: CreateIngestionStatusSchema) -> CreateIngestionStatusResponse:
        """
        Create ingestion status
        :param payload: request body
        """

    @abstractmethod
    async def update_ingestion_status(self, ingestion_id: int, payload: UpdateIngestionStatusSchema):
        """
        Update ingestion status
        :param ingestion_id: ingestion status record id
        :param payload: request body
        """
