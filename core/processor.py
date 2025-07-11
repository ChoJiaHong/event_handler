from typing import Dict

from core.domain import Event
from core.context import Context
from core.domain.state_manager import State
from handlers.base import BaseHandler

class EventProcessor:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.handlers: Dict[str, BaseHandler] = {}

    def register_handler(self, event_type: str, handler: BaseHandler) -> None:
        self.handlers[event_type] = handler

    async def process(self, event: Event) -> None:
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
