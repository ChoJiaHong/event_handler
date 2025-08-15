from abc import ABC, abstractmethod
from typing import Any

class Repository(ABC):
    @abstractmethod
    async def get(self, key: Any):
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: Any, value: Any) -> None:
        raise NotImplementedError
