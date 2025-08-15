from abc import ABC, abstractmethod

from shared.event import Event
from ..context import Context

class BaseHandler(ABC):
    @abstractmethod
    async def handle(self, event: Event, ctx: Context) -> None:
        """Process an event."""
        raise NotImplementedError
