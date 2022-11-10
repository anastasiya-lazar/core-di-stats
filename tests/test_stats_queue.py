import pytest

from core.api.dtos import IngestionParamsSchema, SubscriberMessageSchema
from core.impl.message_processor import MessageProcessor
from solution.sp.sql_base.models import SubscriberStatusEnum


def get_valid_message(request_id="test_request_id", total_record_count=0, total_failed_count=0, total_success_count=0):
    """ Get valid message """
    return {
        "request_id": request_id,
        "source_id": "str",
        "file_uri": "str",
        "subscriber": "str",
        "status": SubscriberStatusEnum.RUNNING.value,
        "is_error": False,
        "message": "str",
        "total_record_count": total_record_count,
        "total_failed_count": total_failed_count,
        "total_success_count": total_success_count,
        "status_url": "str"
    }


@pytest.mark.asyncio
async def test_message_processor_create(get_db, get_ingest_data_payload):
    msg_processor = MessageProcessor()
    request_id = await get_db.db_insert_new_request(IngestionParamsSchema(**get_ingest_data_payload))
    valid_msg = get_valid_message(request_id=request_id, total_record_count=10, total_failed_count=0,
                                  total_success_count=0)
    valid_schema = SubscriberMessageSchema(**valid_msg)
    await msg_processor(valid_schema, "test_id")
    response_schema = await get_db.db_get_request_status(request_id)
    subscriber_statuses = response_schema.dict().get("subscriber_ingestion_statuses")
    assert subscriber_statuses is not None
    assert len(subscriber_statuses) == 1
    assert subscriber_statuses[0].get("status") == SubscriberStatusEnum.RUNNING.value
    assert subscriber_statuses[0].get("total_record_count") == 10
    assert subscriber_statuses[0].get("total_failed_count") == 0
    assert subscriber_statuses[0].get("total_success_count") == 0


@pytest.mark.asyncio
async def test_message_processor_update(get_db, get_ingest_data_payload):
    msg_processor = MessageProcessor()
    request_id = await get_db.db_insert_new_request(IngestionParamsSchema(**get_ingest_data_payload))
    valid_msg = get_valid_message(request_id=request_id, total_record_count=10, total_failed_count=0,
                                  total_success_count=0)
    valid_schema = SubscriberMessageSchema(**valid_msg)
    await msg_processor(valid_schema, "test_id")

    valid_msg_with_updated_totals = get_valid_message(request_id=request_id, total_record_count=10,
                                                      total_failed_count=0,
                                                      total_success_count=5)
    valid_schema = SubscriberMessageSchema(**valid_msg_with_updated_totals)

    await msg_processor(valid_schema, "test_id")
    response_schema = await get_db.db_get_request_status(request_id)
    subscriber_statuses = response_schema.dict().get("subscriber_ingestion_statuses")

    assert subscriber_statuses is not None
    assert len(subscriber_statuses) == 1
    assert subscriber_statuses[0].get("status") == SubscriberStatusEnum.RUNNING.value
    assert subscriber_statuses[0].get("total_record_count") == 10
    assert subscriber_statuses[0].get("total_failed_count") == 0
    assert subscriber_statuses[0].get("total_success_count") == 5


@pytest.mark.asyncio
async def test_message_processor_not_updating_to_less(get_db, get_ingest_data_payload):
    msg_processor = MessageProcessor()
    request_id = await get_db.db_insert_new_request(IngestionParamsSchema(**get_ingest_data_payload))
    valid_msg = get_valid_message(request_id=request_id, total_record_count=10, total_failed_count=0,
                                  total_success_count=0)
    valid_schema = SubscriberMessageSchema(**valid_msg)
    await msg_processor(valid_schema, "test_id")

    valid_msg_with_updated_totals = get_valid_message(request_id=request_id, total_record_count=10,
                                                      total_failed_count=0, total_success_count=5)
    valid_schema = SubscriberMessageSchema(**valid_msg_with_updated_totals)

    await msg_processor(valid_schema, "test_id")

    valid_msg_with_updated_totals = get_valid_message(request_id=request_id, total_record_count=10,
                                                      total_failed_count=0, total_success_count=3)
    valid_schema = SubscriberMessageSchema(**valid_msg_with_updated_totals)

    await msg_processor(valid_schema, "test_id")
    response_schema = await get_db.db_get_request_status(request_id)
    subscriber_statuses = response_schema.dict().get("subscriber_ingestion_statuses")

    assert subscriber_statuses is not None
    assert len(subscriber_statuses) == 1
    assert subscriber_statuses[0].get("status") == SubscriberStatusEnum.RUNNING.value
    assert subscriber_statuses[0].get("total_record_count") == 10
    assert subscriber_statuses[0].get("total_failed_count") == 0
    assert subscriber_statuses[0].get("total_success_count") == 5


@pytest.mark.asyncio
async def test_message_processor_updates_status(get_db, get_ingest_data_payload):
    msg_processor = MessageProcessor()
    request_id = await get_db.db_insert_new_request(IngestionParamsSchema(**get_ingest_data_payload))
    valid_msg = get_valid_message(request_id=request_id, total_record_count=10, total_failed_count=0,
                                  total_success_count=0)
    valid_schema = SubscriberMessageSchema(**valid_msg)
    await msg_processor(valid_schema, "test_id")

    valid_msg_with_updated_totals = get_valid_message(request_id=request_id, total_record_count=10,
                                                      total_failed_count=0, total_success_count=10)
    valid_schema = SubscriberMessageSchema(**valid_msg_with_updated_totals)

    await msg_processor(valid_schema, "test_id")
    response_schema = await get_db.db_get_request_status(request_id)
    subscriber_statuses = response_schema.dict().get("subscriber_ingestion_statuses")

    assert subscriber_statuses is not None
    assert len(subscriber_statuses) == 1
    assert subscriber_statuses[0].get("status") == SubscriberStatusEnum.COMPLETED.value
    assert subscriber_statuses[0].get("total_record_count") == 10
    assert subscriber_statuses[0].get("total_failed_count") == 0
    assert subscriber_statuses[0].get("total_success_count") == 10

