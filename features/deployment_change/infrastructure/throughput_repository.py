"""Concrete throughput repository using optional JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, Mapping

from ..domain.services import ThroughputRepository
from shared import ThroughputKey


class JSONThroughputRepository(ThroughputRepository):
    """Persist throughput values in memory with optional JSON file."""

    def __init__(self, *, initial_data: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None) -> None:
        self._values: Dict[str, Any] = initial_data.copy() if initial_data else {}
        self._path: Optional[Path] = Path(file_path) if file_path else None
        if self._path:
            try:
                if not self._path.exists():
                    self._path.parent.mkdir(parents=True, exist_ok=True)
                    self._path.write_text(json.dumps(self._values, indent=2))
                loaded = json.loads(self._path.read_text())
                if isinstance(loaded, dict):
                    self._values.update(loaded)
            except json.JSONDecodeError:
                pass

    @staticmethod
    def make_key(node_name: str, service_counts: Dict[str, int]) -> str:
        return ThroughputKey(node_name, service_counts).to_string()

    def _normalize_key(self, key: Union[str, Mapping[str, Any], ThroughputKey]) -> str:
        if isinstance(key, ThroughputKey):
            key = key.to_string()
        elif isinstance(key, Mapping):
            key = self.make_key(key.get("node"), dict(key.get("services", {})))
        if ":" not in key:
            return key
        prefix, rest = key.split(":", 1)
        parts = [p for p in rest.split(",") if p]
        if not parts:
            return prefix
        return f"{prefix}:{','.join(sorted(parts))}"

    async def get(self, key: Union[str, Mapping[str, Any], ThroughputKey], category: Optional[str] = None) -> Optional[int]:
        key = self._normalize_key(key)
        value = self._values.get(key)
        if category is None:
            if isinstance(value, dict) and len(value) == 1:
                inner = next(iter(value.values()))
                return inner.get("throughput") if isinstance(inner, dict) else None
            return value if not isinstance(value, dict) else None
        if isinstance(value, dict):
            inner = value.get(category)
            return inner.get("throughput") if isinstance(inner, dict) else None
        return None

    async def save(self, key: Union[str, Mapping[str, Any], ThroughputKey], throughput: int, category: Optional[str] = None) -> None:
        key = self._normalize_key(key)
        if category is None:
            self._values[key] = throughput
        else:
            bucket = self._values.setdefault(key, {})
            if not isinstance(bucket, dict):
                bucket = {}
                self._values[key] = bucket
            entry = bucket.setdefault(category, {})
            if not isinstance(entry, dict):
                entry = {}
                bucket[category] = entry
            entry["throughput"] = throughput
        if self._path:
            self._path.write_text(json.dumps(self._values, indent=2))
