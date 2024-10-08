from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String, func, JSON, UniqueConstraint)

Base = declarative_base()


class FilterCondition(BaseModel):
    match: Literal['exact', 'contains', 'startsWith', 'endsWith', 'larger', 'smaller']


class FilterParams(BaseModel):
    attribute_name: str
    value: str
    condition: FilterCondition = FilterCondition(match='exact')


class RequestStatusEnum(Enum):
    STARTED = "Started"
    SUBMITTED = "Submitted"
    COMPLETE = "Completed"
    FAILED = "Failed"


class IngestionStatusEnum(Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


class SubscriberStatusEnum(Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


class IngestionRequestFilter(Base):
    __tablename__ = "ingestion_request_filter"

    id = Column(Integer, primary_key=True)
    request_id = Column(String(128), ForeignKey("ingestion_request_status.id"))
    attribute = Column(String(80))
    value = Column(String(256))
    condition = Column(String(64))

    @classmethod
    def from_request_param(cls, param: FilterParams, request_id: str):
        return cls(
            request_id=request_id,
            attribute_name=param.attribute_name,
            value=param.value,
            condition=param.condition.match
        )


class SubscriberIngestionStatus(Base):
    __tablename__ = "subscriber_ingestion_status"

    id = Column(Integer, primary_key=True)
    request_id = Column(String(128), ForeignKey("ingestion_request_status.id"))
    source_id = Column(String(128))
    file_uri = Column(String(256))
    subscriber = Column(String(128))
    status = Column(String(80), default=SubscriberStatusEnum.PENDING)
    is_error = Column(Boolean, default=False)
    message = Column(String(256), default="")
    total_record_count = Column(Integer, default=0)
    total_failed_count = Column(Integer, default=0)
    total_success_count = Column(Integer, default=0)
    status_url = Column(String(256), default="")
    last_stat_updated = Column(DateTime(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("request_id", "source_id", "subscriber", "file_uri",
                         name="unique_subscriber_ingestion_status"),
    )


class IngestionStatus(Base):
    __tablename__ = "ingestion_status"

    request_id = Column(String(128), ForeignKey("ingestion_request_status.id"), primary_key=True)
    source_id = Column(String(128), primary_key=True)
    file_uri = Column(String(256))
    entity_type = Column(String(80))
    status = Column(String(80), default=IngestionStatusEnum.RUNNING.value)
    is_error = Column(Boolean, default=False)
    message = Column(String(256), default="")
    total_record_count = Column(Integer, default=0)
    total_failed_count = Column(Integer, default=0)
    total_success_count = Column(Integer, default=0)
    source_queue_name = Column(String(256))
    last_stat_updated = Column(DateTime(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("request_id", "source_id", name="request_source_uc"),
    )


class IngestionRequestStatus(Base):
    __tablename__ = "ingestion_request_status"

    id = Column(String(128), primary_key=True, default=lambda: uuid4().hex)
    tenant_id = Column(String(80))
    app_id = Column(String(80))
    entity_type = Column(String(80))
    src_type = Column(String(80))
    is_batch_required = Column(Boolean, default=False)
    batch_size = Column(Integer, default=0)
    subscriber_name = Column(JSON)
    enrich_oncreation = Column(Boolean, default=False)
    status = Column(String(80), default=RequestStatusEnum.STARTED.value)
    start_time = Column(DateTime, default=lambda: datetime.now(), )
    end_time = Column(DateTime, default=None)
    ingestion_statuses = relationship(IngestionStatus,
                                      primaryjoin="IngestionRequestStatus.id==IngestionStatus.request_id",
                                      lazy="joined")
    subscriber_ingestion_statuses = relationship(
        SubscriberIngestionStatus,
        primaryjoin="IngestionRequestStatus.id==SubscriberIngestionStatus.request_id", lazy="joined")
    filters = relationship(IngestionRequestFilter,
                           primaryjoin="IngestionRequestStatus.id==IngestionRequestFilter.request_id", lazy="joined")
