import asyncio
from enum import Enum

class State(Enum):
    STABLE = "stable"
    ADJUSTING = "adjusting"

class StateManager:
    def __init__(self):
        self.state = State.STABLE
        self._lock = asyncio.Lock()

    async def try_enter_adjusting(self) -> bool:
        async with self._lock:
            if self.state == State.ADJUSTING:
                return False
            self.state = State.ADJUSTING
            return True

    async def exit_adjusting(self) -> None:
        async with self._lock:
            self.state = State.STABLE
