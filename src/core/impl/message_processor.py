import traceback

from typing import Dict, Callable
from bst_core.shared.logger import get_logger

from core.api.dtos import SubscriberMessageSchema
from core.api.message_processor import StatsProcessor
from solution.profile import profile

logger = get_logger(__name__)


class MessageProcessor(StatsProcessor):
    def __init__(self) -> None:
        self._db = profile.db_client

    async def __call__(self, queue_message: SubscriberMessageSchema, message_id: str) -> None:
        logger.info(f"Message: \n{queue_message}")
        if record_id := await self._db.db_create_or_update_subscriber_ingestion_status(queue_message):
            logger.info(f"Created subscriber ingestion status with id: {record_id}")
