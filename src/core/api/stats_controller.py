from abc import ABC, abstractmethod

from core.api.dtos import (IngestionParamsSchema, StatusResponseSchema, IngestProgressDataResponse,
                           CreateIngestionStatusSchema, CreateIngestionStatusResponse, UpdateIngestionStatusSchema,
                           GetIngestionStatusSchema)


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
    async def update_ingestion_status(self, request_id: str, source_id: str, payload: UpdateIngestionStatusSchema):
        """
        Update ingestion status
        :param request_id: request id
        :param source_id: source id
        :param payload: request body
        """

    @abstractmethod
    async def get_ingestion_status(self, request_id: str, source_id: str) -> GetIngestionStatusSchema:
        """
        Get ingestion status
        :param request_id: request id
        :param source_id: source id
        :return: GetIngestionStatusSchema
        """
