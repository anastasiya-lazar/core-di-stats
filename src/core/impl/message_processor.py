import traceback

from typing import Dict, Callable
from bst_core.shared.logger import get_logger

from core.api.dtos import SubscriberMessageSchema
from core.api.message_processor import StatsProcessor
from solution.profile import profile

logger = get_logger(__name__)


def _validation(func: Callable) -> Callable:
    def wrap(self, data):
        try:
            return func(self, data)
        except Exception as exc:
            logger.error(f"[Safe validation] {exc!s}\n\n{traceback.format_exc()}")
    return wrap


class MessageProcessor(StatsProcessor):
    def __init__(self) -> None:
        self._db = profile.db_client

    async def __call__(self, queue_message: Dict, message_id: str) -> None:
        parsed_message = self._parse_input_message(queue_message)
        if not parsed_message:
            return
        logger.info(f"MessageProcessor: {parsed_message}")
        record = await self._db.db_create_subscriber_ingestion_status(parsed_message)
        if record == 'Error':
            logger.error(f"Failed to create subscriber ingestion status for {parsed_message}")
        else:
            logger.info(f"Created subscriber ingestion status with id {record}")

    @_validation
    def _parse_input_message(self, message: Dict) -> SubscriberMessageSchema:
        logger.info(f"Message received: {message}")
        return SubscriberMessageSchema(**message)
