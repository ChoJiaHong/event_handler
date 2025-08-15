from abc import ABC, abstractmethod
from typing import Any

from .event import Event


class BaseHandler(ABC):
    @abstractmethod
    async def handle(self, event: Event, ctx: Any) -> None:
        """Process an event."""
        raise NotImplementedError
