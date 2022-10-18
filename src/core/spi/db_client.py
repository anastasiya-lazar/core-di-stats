from abc import ABC, abstractmethod

from core.api.dtos import (IngestionParamsSchema, StatusResponseSchema, CreateIngestionStatusSchema,
                           UpdateIngestionStatusSchema)


class DBClientSPI(ABC):

    @abstractmethod
    def db_insert_new_request(self, payload: IngestionParamsSchema) -> str:
        """
        Handle incoming requests from mediator to ingest data into the DB
        :param payload: request body
        :return: request ID
        """

    @abstractmethod
    def db_get_request_status(self, request_id: str) -> StatusResponseSchema:
        """
        Get status of request
        :param request_id:
        """

    @abstractmethod
    def db_create_ingestion_status(self, payload: CreateIngestionStatusSchema) -> str:
        """
        Create ingestion status
        :param payload: request body
        """

    @abstractmethod
    def db_update_ingestion_status(self, request_id: str, source_id: str, payload: UpdateIngestionStatusSchema):
        """
        Update ingestion status
        :param request_id: request id
        :param source_id: source id
        :param payload: request body
        """

    @abstractmethod
    def db_get_ingestion_status(self, request_id: str, source_id: str):
        """
        Get ingestion status
        :param request_id: request id
        :param source_id: source id
        """
