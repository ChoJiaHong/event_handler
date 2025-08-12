from abc import ABC, abstractmethod

class Dispatcher(ABC):
    """Send commands to external agents."""

    @abstractmethod
    async def dispatch(self, frequency: int) -> None:
        """Dispatch the new frequency value."""
        raise NotImplementedError
