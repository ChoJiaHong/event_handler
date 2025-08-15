from abc import ABC, abstractmethod
from typing import Any

class Validator(ABC):
    """Interface for data validators."""
    @abstractmethod
    def validate(self, data: Any) -> bool:  # returns True if valid
        raise NotImplementedError

__all__ = ["Validator"]
