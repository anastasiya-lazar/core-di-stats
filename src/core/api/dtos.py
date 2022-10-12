from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from solution.sp.sql_base.models import IngestionStatusEnum, RequestStatusEnum


class IngestionParamsSchema(BaseModel):
    tenant_id: str
    app_id: str
    entity_type: str
    src_type: str
    is_batch_required: bool
    batch_size: int
    subscriber_name: List[str] = []
    enrich_oncreation: bool


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

    class Config:
        orm_mode = True
        use_enum_values = True


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
    id: int


class UpdateIngestionStatusSchema(BaseModel):
    file_uri: str
    entity_type: str
    status: IngestionStatusEnum = IngestionStatusEnum.RUNNING
    is_error: bool
    message: str
    total_record_count: int
    total_failed_count: int
    total_success_count: int

    class Config:
        orm_mode = True
        use_enum_values = True

