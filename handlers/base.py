from abc import ABC, abstractmethod

from core.domain import Event
from core.context import Context

class BaseHandler(ABC):
    @abstractmethod
    async def handle(self, event: Event, ctx: Context) -> None:
        """Process an event."""
        raise NotImplementedError
