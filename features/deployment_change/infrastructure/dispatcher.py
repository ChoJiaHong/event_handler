from ..domain.services import Dispatcher as DispatcherInterface


class InMemoryDispatcher(DispatcherInterface):
    """Store dispatched frequency for inspection in tests."""

    def __init__(self) -> None:
        self.last_dispatched = None

    async def dispatch(self, frequency: int) -> None:
        self.last_dispatched = frequency
