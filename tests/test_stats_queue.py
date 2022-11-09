from unittest import TestCase
import pytest

from core.api.dtos import IngestionParamsSchema
from core.impl.message_processor import MessageProcessor
from solution.sp.sql_base.models import SubscriberStatusEnum


class MessageProcessorTestCase(TestCase):
    async def setUp(self) -> None:
        self.msg_processor = MessageProcessor()
        self.request_id = await pytest._db.db_insert_new_request(IngestionParamsSchema(**ingest_data_payload))

    async def test_message_processor_create(self):
        await self.msg_processor(get_valid_message(self.request_id, 10, 0, 0), "test_id")
        subscriber_statuses = await pytest._db.db_get_request_status(
            self.request_id).subscriber_ingestion_statuses
        self.assertEqual(
            subscriber_statuses is not None,
            True)
        self.assertEqual(len(subscriber_statuses), 1)
        self.assertEqual(subscriber_statuses[0].status, SubscriberStatusEnum.RUNNING.value)
        self.assertEqual(subscriber_statuses[0].total_record_count, 10)
        self.assertEqual(subscriber_statuses[0].total_failed_count, 0)
        self.assertEqual(subscriber_statuses[0].total_success_count, 0)

    async def test_message_processor_update(self):
        await self.msg_processor(get_valid_message(self.request_id, 10, 0, 5), "test_id")
        subscriber_statuses_after_update = await pytest._db.db_get_request_status(
            self.request_id).subscriber_ingestion_statuses
        self.assertEqual(subscriber_statuses_after_update[0].total_record_count, 10)
        self.assertEqual(subscriber_statuses_after_update[0].total_failed_count, 0)
        self.assertEqual(subscriber_statuses_after_update[0].total_success_count, 5)
        self.assertEqual(len(subscriber_statuses_after_update), 1)

    async def test_message_processor_not_updating_to_less(self):
        await self.msg_processor(get_valid_message(self.request_id, 10, 0, 2), "test_id")
        subscriber_statuses_without_changes = await pytest._db.db_get_request_status(
            self.request_id).subscriber_ingestion_statuses
        self.assertEqual(subscriber_statuses_without_changes[0].total_record_count, 10)
        self.assertEqual(subscriber_statuses_without_changes[0].total_failed_count, 0)
        self.assertEqual(subscriber_statuses_without_changes[0].total_success_count, 5)
        self.assertEqual(len(subscriber_statuses_without_changes), 1)
        self.assertEqual(subscriber_statuses_without_changes[1].status, SubscriberStatusEnum.RUNNING.value)

    async def test_message_processor_updates_status(self):
        await self.msg_processor(get_valid_message(self.request_id, 10, 0, 10), "test_id")
        subscriber_statuses_after_creating_new = await pytest._db.db_get_request_status(
            self.request_id).subscriber_ingestion_statuses
        self.assertEqual(len(subscriber_statuses_after_creating_new), 2)
        self.assertEqual(subscriber_statuses_after_creating_new[1].total_record_count, 10)
        self.assertEqual(subscriber_statuses_after_creating_new[1].total_failed_count, 0)
        self.assertEqual(subscriber_statuses_after_creating_new[1].total_success_count, 10)
        self.assertEqual(subscriber_statuses_after_creating_new[1].status, SubscriberStatusEnum.COMPLETED.value)


