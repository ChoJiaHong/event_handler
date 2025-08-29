from abc import ABC, abstractmethod
from typing import Dict

class PressureTester(ABC):
    """Interface for performing load tests."""

    @abstractmethod
    async def load_test(self, deployment_hash: str) -> int:
        """Return measured throughput for the deployment."""
        raise NotImplementedError

    @abstractmethod
    async def get_last_service_throughputs(self) -> Dict[str, int]:
        """Return detailed service throughputs from the last test."""
        raise NotImplementedError
