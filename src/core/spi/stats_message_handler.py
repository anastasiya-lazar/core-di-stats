from abc import ABC, abstractmethod
from typing import Callable, Dict


class StatsMessageHandlerSPI(ABC):
    """
    Base class for connect to the stats di queue and process message from it
    """

    def __init__(self) -> None:
        self._handler = None

    def set_msg_processor(self, handler: Callable[[Dict], None]) -> None:
        """
        Set handler, which will handle messages from the Qeuue

        The finishing of given handler without errors will be marker to success message processing.
        Otherwise - queue will be notified, that worker fails to process this message
        :param handler: handler - act as function, which will be called with input body
        :return:
        """
        self._handler = handler

    @abstractmethod
    async def run(self) -> None:
        """
        Start infinity loop of the receiving messages
        """
