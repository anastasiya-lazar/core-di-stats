from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IngestionParamsSchema(BaseModel):
    tenant_id: str
    app_id: str
    entity_type: str
    src_type: str
    is_batch_required: bool
    batch_size: int
    enrich_oncreation: bool


class StatusResponseSchema(BaseModel):
    tenant_id: str
    app_id: str
    entity_type: str
    src_type: str
    is_batch_required: bool
    batch_size: int
    enrich_oncreation: bool
    status: str
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        orm_mode = True


class IngestProgressDataResponse(BaseModel):
    request_id: str
