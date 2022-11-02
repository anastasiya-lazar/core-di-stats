import asyncio


from bst_core.shared.basic_logger import get_logger

import config as conf
from core.impl.message_processor import MessageProcessor
from solution.channel.open_telemetry import config_open_telemetry
from solution.channel.rest.app import run_non_block
from solution.profile import profile

logger = get_logger(__name__, conf.LOGGER_LEVEL)


async def main():
    config_open_telemetry()
    logger.info("Worker started")
    msg_processor = MessageProcessor()
    msg_handler = profile.get_stats_message_handler()
    msg_handler.set_msg_processor(msg_processor)
    await msg_handler.run()


if __name__ == '__main__':
    logger.info("Initializing...")
    loop = asyncio.get_event_loop()
    site = run_non_block(loop)

    task_1 = loop.create_task(site.start())
    logger.info("Started healthcheck server")
    task_2 = loop.create_task(main())

    loop.run_forever()
