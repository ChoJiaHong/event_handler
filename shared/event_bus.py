from typing import Dict, Any

from .event import Event
from .state_manager import State
from .base_handler import BaseHandler


class EventBus:
    def __init__(self, ctx: Any):
        self.ctx = ctx
        self.handlers: Dict[str, BaseHandler] = {}

    def register_handler(self, event_type: str, handler: BaseHandler) -> None:
        self.handlers[event_type] = handler

    async def publish(self, event: Event) -> None:
        handler = self.handlers.get(event.type)
        if not handler:
            return
        entered = await self.ctx.state.try_enter_adjusting()
        if not entered:
            return
        try:
            await handler.handle(event, self.ctx)
        finally:
            await self.ctx.state.exit_adjusting()
