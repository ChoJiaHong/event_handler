import logging

from core.domain import Event
from core.context import Context
from .base import BaseHandler

logger = logging.getLogger(__name__)

class HighLatencyHandler(BaseHandler):
    """Handle high latency events."""

    async def handle(self, event: Event, ctx: Context) -> None:
        logger.info("High latency event received: %s", event.payload)
        logger.info("No action taken in stub handler")
