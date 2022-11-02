import asyncio
import json
import logging
from datetime import datetime
from json import JSONDecodeError

from bst_core.shared.logger import get_logger
from config import MAX_DELIVERY_COUNT, OTEL_CONTEXT_NAME
from core.impl.health_check import LoopBeatCheck, MessageProceedCheck
from core.spi.stats_message_handler import StatsMessageHandlerSPI
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import \
    TraceContextTextMapPropagator
from pydantic import ValidationError

from azure.servicebus import (ServiceBusConnectionStringProperties,
                              ServiceBusReceivedMessage, exceptions,
                              parse_connection_string)
from azure.servicebus.aio import AutoLockRenewer, ServiceBusClient
from azure.servicebus.aio.management import ServiceBusAdministrationClient
from azure.servicebus.exceptions import ServiceBusQuotaExceededError

uamqp_logger = get_logger("uamqp")
uamqp_logger.setLevel("ERROR")
logger = get_logger(__name__)
uamqp_logger = logging.getLogger("uamqp")
uamqp_logger.setLevel(logging.ERROR)

tracer = trace.get_tracer(__name__)


async def _renewable_track(_, e):
    try:
        logger.warn(f"Renew lock failed", exc_info=e)
    except:
        logger.warn(f"Renew lock failed for unknown reason")


class StatsMessageHandlerSP(StatsMessageHandlerSPI):
    def __init__(self, connection_string: str):
        super().__init__()
        self._connection_string = connection_string
        self._queue_is_full = False
        self._queue_full_count = 0
        self._lim_delay_count = 8
        self._max_delivery_count = MAX_DELIVERY_COUNT

    def _create_context(self, raw_msg: ServiceBusReceivedMessage):
        if not raw_msg.application_properties:
            return None
        if OTEL_CONTEXT_NAME not in raw_msg.application_properties:
            return None
        carrier = json.loads(raw_msg.application_properties.get(OTEL_CONTEXT_NAME))
        return TraceContextTextMapPropagator().extract(carrier=carrier)

    async def run(self, time_limit: int = 300) -> None:
        logger.info("Init handling...")
        connection_info: ServiceBusConnectionStringProperties = parse_connection_string(self._connection_string)
        logger.debug(
            f"Read queue configurations: "
            f"name={connection_info.entity_path}, namespace={connection_info.fully_qualified_namespace}"
        )
        try:
            queue_props_client = ServiceBusAdministrationClient.from_connection_string(conn_str=self._connection_string)
            async with queue_props_client:
                queue_props = await queue_props_client.get_queue(connection_info.entity_path)
                self._max_delivery_count = queue_props.max_delivery_count
        except Exception as e:
            logger.error(e, exc_info=True)
        logger.info(f'Set _max_delivery_count to {self._max_delivery_count}')

        while True:
            client = ServiceBusClient.from_connection_string(conn_str=self._connection_string, logging_enable=True)

            async with client:
                logger.info("Inited queue client")
                lock_renewer = AutoLockRenewer(max_lock_renewal_duration=900, on_lock_renew_failure=_renewable_track)
                receiver = client.get_queue_receiver(queue_name=connection_info.entity_path, auto_lock_renewer=lock_renewer)
                async with receiver:
                    logger.info("Inited receiver")

                    async def handle_single_msg(raw_msg: ServiceBusReceivedMessage):
                        logger.debug(f"New message {raw_msg} fetched from queue")
                        try:
                            with tracer.start_as_current_span(name="handler", context=self._create_context(raw_msg)) as span:
                                raw_msg_body = next(raw_msg.body)
                                span.set_attribute("message", raw_msg_body)
                                msg = json.loads(raw_msg_body)
                                span.set_attribute("request_id", msg.get('request_id'))
                                logger.debug(f"send to process {msg=}")
                                await self._handler(msg, raw_msg.message_id)
                        except ValidationError as ve:
                            logger.error("Data validation error", exc_info=ve)
                            await receiver.dead_letter_message(
                                raw_msg, reason="invalid",
                                error_description=str(ve)
                            )
                            await MessageProceedCheck().abandon()
                        except JSONDecodeError as jde:
                            logger.error("Data corrupted error", exc_info=jde)
                            await receiver.dead_letter_message(
                                raw_msg, reason="corrupted",
                                error_description=str(jde)
                            )
                            await MessageProceedCheck().abandon()
                        except Exception as e:
                            try:
                                logger.error("Can not parse message from the queue", exc_info=e)
                                if isinstance(e, ServiceBusQuotaExceededError):
                                    self._queue_is_full = True
                                    if self._queue_full_count >= self._lim_delay_count:
                                        await MessageProceedCheck().abandon()
                                if raw_msg.delivery_count + 1 >= self._max_delivery_count:
                                    await receiver.dead_letter_message(
                                        raw_msg, reason="transient",
                                        error_description=str(e)
                                    )
                                    logger.error(
                                        "Error during processing message. Message will be put to dead letter queue",
                                        exc_info=e
                                    )
                                else:
                                    await receiver.abandon_message(raw_msg)
                                    await MessageProceedCheck().abandon()
                                    logger.error(
                                        "Error during processing message. Message will be returned to the queue ",
                                        exc_info=e
                                    )
                            except exceptions.ServiceBusError as sb_error:
                                await MessageProceedCheck().queue_error()
                                logger.error("Can not receiver.abandon_message", exc_info=sb_error)
                        else:
                            try:
                                await receiver.complete_message(raw_msg)
                                await MessageProceedCheck().complete()
                                logger.debug("Message {msg} was successes processed")
                            except exceptions.ServiceBusError as sb_error:
                                await MessageProceedCheck().queue_error()
                                logger.error("can not complete message", exc_info=sb_error)

                    start = datetime.now()
                    while (datetime.now() - start).total_seconds() < time_limit:
                        await LoopBeatCheck().loop_beat()
                        self._queue_is_full = False
                        received_msgs = await receiver.receive_messages(max_message_count=256, max_wait_time=8)
                        logger.info(f"received message pack, {len(received_msgs)=}")
                        await asyncio.gather(*map(handle_single_msg, received_msgs))
                        if self._queue_is_full:
                            self._queue_full_count += 1
                            sleep_time = 2 ** min(self._queue_full_count, self._lim_delay_count)
                            logger.info(f"Queue is full. Sleeping {sleep_time}s. ....")
                            await asyncio.sleep(sleep_time)
                            logger.info("Continue to consume from the queue...")
                        else:
                            self._queue_full_count = 0
