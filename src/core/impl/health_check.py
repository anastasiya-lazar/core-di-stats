import asyncio
from abc import ABC
from datetime import datetime, timedelta
from enum import Enum

from config import HEALTH_CHECK_LIST
from core.api.health_check import (
    HealthCheckI,
    HealthCheckStateI,
    HealthCheckTypes,
    HealthPublicState,
)


def on_enable(func):
    async def wrapper(self, *args, **kwargs):
        if self.CHECK_TYPE not in HealthCheckState().enabled_checks:
            return
        await func(self, *args, **kwargs)

    return wrapper


class HealthCheckBase(HealthCheckI, ABC):
    async def get_state(self) -> dict:
        try:
            return HealthCheckState().state[self.CHECK_TYPE.name].copy()
        except KeyError:
            return dict()

    async def set_state(self, new_state: dict) -> None:
        HealthCheckState().state.update({self.CHECK_TYPE.name: new_state})

    async def publish_state(self, new_state: HealthPublicState) -> None:
        HealthCheckState().public_state.update({self.CHECK_TYPE.name: new_state})


class LoopBeatCheck(HealthCheckBase):
    CHECK_TYPE = HealthCheckTypes.loop_beat
    CHECK_RANGE_SECONDS = 300

    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(LoopBeatCheck, cls).__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self):
        if hasattr(self, "delta"):
            return
        self.delta = timedelta(seconds=self.CHECK_RANGE_SECONDS)

    @on_enable
    async def loop_beat(self) -> None:
        state = await self.get_state()
        state["last_date"] = datetime.now()
        await self.set_state(state)

    @on_enable
    async def update_state(self) -> None:
        state = await self.get_state()
        last_date = state.get("last_date", datetime.now() - self.delta * 2)

        healthy = datetime.now() - last_date <= timedelta(
            seconds=self.CHECK_RANGE_SECONDS
        )
        info = "Ok"
        if not healthy:
            info = "Maybe loop stuck"

        new_public_state = HealthPublicState(healthy, info)
        state["last_date"] = last_date
        await self.publish_state(new_public_state)


class MessageProceedCheck(HealthCheckBase):
    CHECK_TYPE = HealthCheckTypes.message_proceed
    CHECK_RANGE_SECONDS = 300
    DEGRADED_TH = 0.5
    instance = None

    class EventTypes(Enum):
        complete = 0
        abandon = 1
        dead_letter = 2
        queue_error = 3

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(MessageProceedCheck, cls).__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self):
        if hasattr(self, "delta"):
            return
        self.delta = timedelta(seconds=self.CHECK_RANGE_SECONDS)
        self.last_date = datetime.now()
        self._lock = asyncio.Lock()

    async def _increase_stats(self, event_type: EventTypes) -> None:
        async with self._lock:
            state = await self.get_state()
            state["last_date"] = state.get("last_date")
            if state["last_date"] is None or datetime.now() - state["last_date"] >= self.delta:
                state["last_date"] = datetime.now()
                for event in self.EventTypes:
                    state[event] = 0

            state[event_type] += 1
            await self.set_state(state)

    @on_enable
    async def complete(self) -> None:
        await self._increase_stats(self.EventTypes.complete)

    @on_enable
    async def abandon(self) -> None:
        await self._increase_stats(self.EventTypes.abandon)

    @on_enable
    async def dead_letter(self) -> None:
        await self._increase_stats(self.EventTypes.dead_letter)

    @on_enable
    async def queue_error(self) -> None:
        await self._increase_stats(self.EventTypes.queue_error)

    @on_enable
    async def update_state(self) -> None:
        state = await self.get_state()

        failed = (
                state.get(self.EventTypes.abandon, 0)
                + state.get(self.EventTypes.dead_letter, 0)
                + state.get(self.queue_error, 0)
        )
        all_message = failed + state.get(self.EventTypes.complete, 0)

        healthy = True
        info = "Ok"

        if all_message > 0:
            percent = failed / (failed + state[self.EventTypes.complete])
            healthy = percent < self.DEGRADED_TH
            if not healthy:
                info = f"Greater than {percent} messages abandon or dead letter."

        new_public_state = HealthPublicState(healthy, info)
        await self.publish_state(new_public_state)


class HealthCheckState(HealthCheckStateI):
    HEALTH_CHECKER_CLASSES = {
        HealthCheckTypes.loop_beat: LoopBeatCheck,
        HealthCheckTypes.message_proceed: MessageProceedCheck,
    }

    def __init__(self):
        if hasattr(self, "state"):
            return
        self.state = dict()
        self.public_state = dict()
        self.enabled_checks = [HealthCheckTypes[item] for item in HEALTH_CHECK_LIST]
        self._checkers = [self.HEALTH_CHECKER_CLASSES[checker_type]() for checker_type in self.enabled_checks]

    async def update(self) -> None:
        await asyncio.gather(*(checker.update_state() for checker in self._checkers))
