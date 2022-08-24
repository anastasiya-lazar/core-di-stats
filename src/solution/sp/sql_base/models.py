from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy.orm import declarative_base
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,)

Base = declarative_base()


class RequestStatusEnum(Enum):
    STARTED = "Started"
    SUBMITTED = "Submitted"
    COMPLETE = "Completed"
    FAILED = "Failed"


class IngestionRequestStatus(Base):
    __tablename__ = "ingestion_request_status"

    id = Column(String(128), primary_key=True, default=lambda: uuid4().hex)
    tenant_id = Column(String(80))
    app_id = Column(String(80))
    entity_type = Column(String(80))
    src_type = Column(String(80))
    is_batch_required = Column(Boolean)
    batch_size = Column(Integer)
    enrich_oncreation = Column(Boolean)
    status = Column(String(80), default=RequestStatusEnum.STARTED.value)
    start_time = Column(DateTime, default=lambda: datetime.now(), )
    end_time = Column(DateTime, default=None)


class IngestionRequestFilter(Base):
    __tablename__ = "ingestion_request_filter"

    id = Column(Integer, primary_key=True)
    request_id = Column(String(128), ForeignKey("ingestion_request_status.id"))
    attribute = Column(String(80))
    value = Column(String(256))
    condition = Column(Boolean)


class SubscriberIngestionStatus(Base):
    __tablename__ = "subscriber_ingestion_status"

    id = Column(Integer, primary_key=True)
    request_id = Column(String(128), ForeignKey("ingestion_request_status.id"))
    source_id = Column(String(128))
    file_uri = Column(String(256))
    subscriber = Column(String(128))
    status = Column(String(80))
    is_error = Column(Boolean)
    message = Column(String(256))
    total_record_count = Column(Integer, default=0)
    total_failed_count = Column(Integer, default=0)
    total_success_count = Column(Integer, default=0)
    status_url = Column(String(256))
    last_stat_updated = Column(DateTime())


class IngestionStatus(Base):
    __tablename__ = "ingestion_status"

    id = Column(Integer, primary_key=True)
    request_id = Column(String(128), ForeignKey("ingestion_request_status.id"))
    source_id = Column(String(128))
    file_uri = Column(String(256))
    entity_type = Column(String(80))
    status = Column(String(80))
    is_error = Column(Boolean)
    message = Column(String(256))
    total_record_count = Column(Integer, default=0)
    total_failed_count = Column(Integer, default=0)
    total_success_count = Column(Integer, default=0)
    source_queue_name = Column(String(256))
    last_stat_updated = Column(DateTime())
