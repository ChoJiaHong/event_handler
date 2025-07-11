from abc import ABC, abstractmethod
from typing import Optional, Mapping, Union, Any

class ThroughputRepository(ABC):
    """Persist and retrieve throughput values."""

    @abstractmethod
    async def get(self, key: Union[str, Mapping[str, Any]], category: Optional[str] = None) -> Optional[int]:
        """Retrieve stored throughput."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, key: Union[str, Mapping[str, Any]], throughput: int, category: Optional[str] = None) -> None:
        """Persist throughput information."""
        raise NotImplementedError
