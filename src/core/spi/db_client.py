from abc import ABC, abstractmethod

from core.api.dtos import IngestionParamsSchema, StatusResponseSchema, CreateIngestionStatusSchema


class DBClientSPI(ABC):

    @abstractmethod
    def insert_new_request(self, payload: IngestionParamsSchema) -> str:
        """
        Handle incoming requests from mediator to ingest data into the DB
        :param payload: request body
        :return: request ID
        """

    @abstractmethod
    def get_request_status(self, request_id: str) -> StatusResponseSchema:
        """
        Get status of request
        :param request_id:
        """

    @abstractmethod
    def db_create_ingestion_status(self, payload: CreateIngestionStatusSchema) -> int:
        """
        Create ingestion status
        :param payload: request body
        """
