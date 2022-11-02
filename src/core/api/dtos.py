from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel

from solution.sp.sql_base.models import IngestionStatusEnum, RequestStatusEnum, FilterParams, SubscriberStatusEnum


class IngestionParamsSchema(BaseModel):
    tenant_id: str
    app_id: str
    entity_type: str
    src_type: str
    is_batch_required: bool
    batch_size: int
    subscriber_name: List[str] = []
    enrich_oncreation: bool
    filters: List[FilterParams] = []


class IngestProgressDataResponse(BaseModel):
    request_id: str


class CreateIngestionStatusSchema(BaseModel):
    request_id: str
    source_id: str
    file_uri: str
    entity_type: str
    is_error: bool
    message: str
    total_record_count: int
    total_failed_count: int
    total_success_count: int
    source_queue_name: str


class CreateIngestionStatusResponse(BaseModel):
    creation_status: str


class UpdateIngestionStatusSchema(BaseModel):
    file_uri: Optional[str]
    entity_type: Optional[str]
    status: Optional[IngestionStatusEnum] = IngestionStatusEnum.RUNNING
    is_error: Optional[bool]
    message: Optional[str]
    total_record_count: Optional[int]
    total_failed_count: Optional[int]
    total_success_count: Optional[int]

    class Config:
        orm_mode = True
        use_enum_values = True


class GetIngestionStatusSchema(BaseModel):
    request_id: str
    source_id: str
    file_uri: str
    entity_type: str
    status: IngestionStatusEnum = IngestionStatusEnum.RUNNING
    is_error: bool
    message: str
    total_record_count: int
    total_failed_count: int
    total_success_count: int
    source_queue_name: str
    last_stat_updated: Optional[datetime]

    class Config:
        orm_mode = True
        use_enum_values = True


class GetSubscriberIngestionStatusSchema(BaseModel):
    id: int
    request_id: str
    source_id: str
    file_uri: str
    subscriber: str
    status: IngestionStatusEnum = IngestionStatusEnum.RUNNING
    is_error: bool
    message: str
    total_record_count: int
    total_failed_count: int
    total_success_count: int
    status_url: str
    last_stat_updated: Optional[datetime]

    class Config:
        orm_mode = True
        use_enum_values = True


class StatusResponseSchema(BaseModel):
    tenant_id: str
    app_id: str
    entity_type: str
    src_type: str
    is_batch_required: bool
    batch_size: int
    subscriber_name: List[str] = []
    enrich_oncreation: bool
    status: RequestStatusEnum = RequestStatusEnum.STARTED
    start_time: datetime
    end_time: Optional[datetime]
    ingestion_statuses: Optional[List[GetIngestionStatusSchema]]
    subscriber_ingestion_statuses: Optional[List[GetSubscriberIngestionStatusSchema]]

    class Config:
        orm_mode = True
        use_enum_values = True


class SubscriberMessageSchema(BaseModel):
    request_id: str
    source_id: str
    file_uri: str
    subscriber: str
    status: Optional[SubscriberStatusEnum] = SubscriberStatusEnum.RUNNING
    is_error: Optional[bool]
    message: Optional[str]
    total_record_count: Optional[int] = 0
    total_failed_count: Optional[int] = 0
    total_success_count: Optional[int] = 0
    status_url: Optional[str]

    class Config:
        orm_mode = True
        use_enum_values = True
