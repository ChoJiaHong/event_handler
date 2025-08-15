from typing import Any, Dict

class Config:
    """Simple configuration holder."""
    def __init__(self, values: Dict[str, Any] | None = None) -> None:
        self._values = values or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

config = Config()

__all__ = ["Config", "config"]
