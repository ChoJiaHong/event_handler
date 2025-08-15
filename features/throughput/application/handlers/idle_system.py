from shared.event import Event
from shared.logger import get_logger
from ..context import Context
from .base import BaseHandler

logger = get_logger(__name__)

class IdleSystemHandler(BaseHandler):
    """Handle idle system events."""

    async def handle(self, event: Event, ctx: Context) -> None:
        logger.info("Idle system event received: %s", event.payload)
        logger.info("No action taken in stub handler")
