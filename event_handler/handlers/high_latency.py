import logging

from ..event import Event
from ..context import Context
from .base import BaseHandler

logger = logging.getLogger(__name__)


class HighLatencyHandler(BaseHandler):
    """Handle high latency events."""

    async def handle(self, event: Event, ctx: Context) -> None:
        """Placeholder implementation."""
        logger.info("High latency event received: %s", event.payload)
        # Real logic will decrease frequency and schedule retest
        logger.info("No action taken in stub handler")
