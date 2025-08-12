from abc import ABC, abstractmethod

class AdjustmentStrategy(ABC):
    """Compute new request frequency based on throughput."""

    @abstractmethod
    async def compute_frequency(self, throughput: int) -> int:
        """Return a request frequency derived from throughput."""
        raise NotImplementedError
