from abc import ABC, abstractmethod

class PressureTester(ABC):
    """Interface for performing load tests."""

    @abstractmethod
    async def load_test(self, deployment_hash: str) -> int:
        """Return measured throughput for the deployment."""
        raise NotImplementedError
