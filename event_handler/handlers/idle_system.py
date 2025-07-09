from ..event import Event
from ..context import Context
from .base import BaseHandler


class IdleSystemHandler(BaseHandler):
    """Handle idle system events."""

    async def handle(self, event: Event, ctx: Context) -> None:
        """Placeholder implementation."""
        # Real logic will reduce or pause frequency
        pass
