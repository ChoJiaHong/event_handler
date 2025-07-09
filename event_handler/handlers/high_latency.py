from ..event import Event
from ..context import Context
from .base import BaseHandler


class HighLatencyHandler(BaseHandler):
    """Handle high latency events."""

    async def handle(self, event: Event, ctx: Context) -> None:
        """Placeholder implementation."""
        # Real logic will decrease frequency and schedule retest
        pass
