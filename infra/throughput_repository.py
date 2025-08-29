"""Concrete throughput repository using optional JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, Mapping

from core.services import ThroughputRepository
from utils.helpers import ThroughputKey


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
            # 優先返回 "total" 欄位的值
            if isinstance(value, dict):
                if "total" in value and isinstance(value["total"], dict):
                    return value["total"].get("throughput")
                # 向後兼容：如果只有一個欄位且不是服務分類格式
                if len(value) == 1:
                    inner = next(iter(value.values()))
                    return inner.get("throughput") if isinstance(inner, dict) else inner
            # 向後兼容：直接數值
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

    async def save_service_throughputs(
        self, 
        key: Union[str, Mapping[str, Any], ThroughputKey], 
        service_throughputs: Dict[str, int]
    ) -> None:
        """
        儲存多服務的吞吐量資料
        
        Input:
        - key: 部署金鑰
        - service_throughputs: {service_type: throughput}
        """
        key = self._normalize_key(key)
        
        # 確保有一個字典結構來儲存服務資料
        if key not in self._values:
            self._values[key] = {}
        elif not isinstance(self._values[key], dict):
            self._values[key] = {}
        
        # 為每個服務分別儲存
        for service_type, throughput in service_throughputs.items():
            self._values[key][service_type] = {"throughput": throughput}
        
        # 儲存總和到特殊的 "total" 欄位
        total_throughput = sum(service_throughputs.values())
        self._values[key]["total"] = {"throughput": total_throughput}
        
        # 寫入檔案
        if self._path:
            self._path.write_text(json.dumps(self._values, indent=2))

    async def get_service_throughputs(
        self, 
        key: Union[str, Mapping[str, Any], ThroughputKey]
    ) -> Dict[str, int]:
        """
        獲取多服務的吞吐量資料
        
        Output:
        - {service_type: throughput}
        """
        key = self._normalize_key(key)
        value = self._values.get(key, {})
        
        if isinstance(value, dict):
            # 提取所有服務的吞吐量
            service_throughputs = {}
            for service_type, service_data in value.items():
                if isinstance(service_data, dict) and 'throughput' in service_data:
                    service_throughputs[service_type] = service_data['throughput']
            return service_throughputs
        
        return {}
