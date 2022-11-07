from unittest import TestCase

from core.api.dtos import SubscriberMessageSchema, IngestionParamsSchema
from core.impl.message_processor import MessageProcessor
from solution.sp.sql_base.models import SubscriberStatusEnum

MESSAGE_FROM_QUEUE = {
    "request_id": "test_request_id",
    "source_id": "str",
    "file_uri": "str",
    "subscriber": "str",
    "status": SubscriberStatusEnum.RUNNING.value,
    "is_error": False,
    "message": "str",
    "total_record_count": 0,
    "total_failed_count": 0,
    "total_success_count": 0,
    "status_url": "str"
}

INGEST_DATA_PAYLOAD = {
  "tenant_id": "string",
  "app_id": "string",
  "entity_type": "string",
  "src_type": "string",
  "is_batch_required": True,
  "batch_size": 0,
  "subscriber_name": [],
  "enrich_oncreation": True,
  "filters": []
}


class MessageProcessorTestCase(TestCase):
    async def setUp(self) -> None:
        self.msg_processor = MessageProcessor()
        self.request_id = await self.msg_processor._db.db_insert_new_request(IngestionParamsSchema(**INGEST_DATA_PAYLOAD))
        MESSAGE_FROM_QUEUE['request_id'] = self.request_id
        self.correct_msg = SubscriberMessageSchema(**MESSAGE_FROM_QUEUE)

    async def test_message_processor(self):
        await self.msg_processor(self.correct_msg, "test_id")
        subscriber_statuses = await self.msg_processor._db.db_get_request_status(
            self.request_id).subscriber_ingestion_statuses
        self.assertEqual(
            subscriber_statuses is not None,
            True)
        self.assertEqual(len(subscriber_statuses), 1)
        self.assertEqual(subscriber_statuses[0].status, SubscriberStatusEnum.RUNNING.value)
        self.assertEqual(subscriber_statuses[0].total_record_count, 0)

        self.correct_msg.total_record_count = 10
        await self.msg_processor(self.correct_msg, "test_id")
        subscriber_statuses_after_update = await self.msg_processor._db.db_get_request_status(
            self.request_id).subscriber_ingestion_statuses
        self.assertEqual(subscriber_statuses_after_update[0].total_record_count, 10)
        self.assertEqual(len(subscriber_statuses_after_update), 1)

        self.correct_msg.total_record_count = 5
        await self.msg_processor(self.correct_msg, "test_id")
        subscriber_statuses_after_update = await self.msg_processor._db.db_get_request_status(
            self.request_id).subscriber_ingestion_statuses
        self.assertEqual(subscriber_statuses_after_update[0].total_record_count, 10)
        self.assertEqual(len(subscriber_statuses_after_update), 1)

        self.correct_msg.source_id = "test_source_id"
        await self.msg_processor(self.correct_msg, "test_id")
        subscriber_statuses_after_creating_new = await self.msg_processor._db.db_get_request_status(
            self.request_id).subscriber_ingestion_statuses
        self.assertEqual(len(subscriber_statuses_after_creating_new), 2)
        self.assertEqual(subscriber_statuses_after_creating_new[1].total_record_count, 5)

    async def tearDown(self) -> None:
        self.msg_processor._db.session.close_all()
        self.msg_processor._db.engine.dispose()
        self.msg_processor._db.engine = None
        self.msg_processor._db.session = None
        import gc
        gc.collect()

