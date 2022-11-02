import dataclasses
from abc import ABC, abstractmethod
from enum import Enum


class HealthCheckTypes(Enum):
    loop_beat = 0
    message_proceed = 1


@dataclasses.dataclass
class HealthPublicState:
    healthy: bool
    info: str


class HealthCheckStateI(ABC):

    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(HealthCheckStateI, cls).__new__(cls, *args, **kwargs)
        return cls.instance


class HealthCheckI(ABC):
    check_type: HealthCheckTypes

    @abstractmethod
    async def get_state(self) -> dict:
        """
        return internal state for the health check from HealthCheckStateSPI
        """
        pass

    @abstractmethod
    async def set_state(self, new_state: dict) -> None:
        """
        save internal state
        """

    @abstractmethod
    async def publish_state(self, new_state: HealthPublicState) -> None:
        """
        save public state
        """

    @abstractmethod
    async def update_state(self) -> None:
        """
        Update state
        :return:
        """
