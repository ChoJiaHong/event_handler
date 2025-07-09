"""Utility for persisting and querying throughput data.

The original implementation only kept an in-memory dictionary mapping a
deployment hash to an integer throughput value.  Some tests still rely on that
behaviour, but the recorder now also understands a more complex JSON structure
where each key can contain sub categories (e.g. ``pose`` or ``gesture``) with a
``throughput`` field.  An example of the supported JSON format is::

    {
        "node1:gesture=2,pose=1": {
            "pose": {"throughput": 20},
            "gesture": {"throughput": 30}
        },
        "node2:object=1,pose=1": {
            "pose": {"throughput": 40},
            "object": {"throughput": 15}
        }
    }

When a ``file_path`` is provided, the recorder will load the JSON data from the
file at initialisation time and persist updates back to the same file.
``get`` and ``save`` accept an optional ``category`` argument for accessing the
nested values.  When ``category`` is omitted the behaviour is backwards
compatible with the original implementation and simply treats the value as a
plain integer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ThroughputRecorder:
    """Persist and retrieve throughput values."""

    def __init__(self, *, initial_data: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None) -> None:
        self._values: Dict[str, Any] = initial_data.copy() if initial_data else {}
        self._path: Optional[Path] = Path(file_path) if file_path else None
        if self._path and self._path.exists():
            try:
                loaded = json.loads(self._path.read_text())
                if isinstance(loaded, dict):
                    self._values.update(loaded)
            except json.JSONDecodeError:
                # Invalid json, ignore and start fresh
                pass

    async def get(self, key: str, category: Optional[str] = None) -> Optional[int]:
        value = self._values.get(key)
        if category is None:
            if isinstance(value, dict):
                # if the stored value has a single category, return its throughput
                if len(value) == 1:
                    inner = next(iter(value.values()))
                    return inner.get("throughput") if isinstance(inner, dict) else None
                return None
            return value
        if not isinstance(value, dict):
            return None
        inner = value.get(category)
        if isinstance(inner, dict):
            return inner.get("throughput")
        return None

    async def save(self, key: str, throughput: int, category: Optional[str] = None) -> None:
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

