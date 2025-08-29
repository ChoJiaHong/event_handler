"""Prometheus client for querying metrics via HTTP API."""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Any
from prometheus_api_client import PrometheusConnect


class PrometheusClient:
    """Retrieve metrics from a Prometheus server."""

    def __init__(self, base_url: str = "http://prometheus-operated.prometheus.svc.cluster.local:9090") -> None:
        self._client = PrometheusConnect(url=base_url, disable_ssl=True)

    async def query(self, promql: str) -> dict:
        """Execute a PromQL query and return parsed JSON data."""
        def _fetch() -> dict:
            return self._client.custom_query(query=promql)
        
        return await asyncio.to_thread(_fetch)

    async def get_rps_by_service_and_node(self, service_type: str, node_name: str, port_suffix: str = None) -> Optional[float]:
        """
        根據 service type 和 node name 取得 RPS (requests per second) 指標
        
        Args:
            service_type: 服務類型 (如 'pose', 'gesture', 'object')
            node_name: 節點名稱 (如 'workgpu', 'workergpu2')
            port_suffix: Pod 的 port 後綴 (如 '30501'), 如果為 None 則會匹配任何 port
            
        Returns:
            當前的 RPS 值，如果找不到則返回 None
        """
        if port_suffix:
            pod_name = f"{service_type}-{node_name}-{port_suffix}"
            query = f'requests_per_second{{job="default/pose-podmonitor", pod="{pod_name}"}}'
        else:
            # 使用正則表達式匹配任何 port
            pod_pattern = f"{service_type}-{node_name}-.*"
            query = f'requests_per_second{{job="default/pose-podmonitor", pod=~"{pod_pattern}"}}'
        
        result = await self.query(query)
        
        if result and len(result) > 0:
            # 如果有多個結果，返回第一個的值
            first_result = result[0]
            return float(first_result["value"][1])
        
        return None

    async def get_cps_by_service_and_node(self, service_type: str, node_name: str, port_suffix: str = None) -> Optional[float]:
        """
        根據 service type 和 node name 取得 RPS (requests per second) 指標
        
        Args:
            service_type: 服務類型 (如 'pose', 'gesture', 'object')
            node_name: 節點名稱 (如 'workgpu', 'workergpu2')
            port_suffix: Pod 的 port 後綴 (如 '30501'), 如果為 None 則會匹配任何 port
            
        Returns:
            當前的 RPS 值，如果找不到則返回 None
        """
        if port_suffix:
            pod_name = f"{service_type}-{node_name}-{port_suffix}"
            query = f'completed_requests_per_second{{job="default/pose-podmonitor", pod="{pod_name}"}}'
        else:
            # 使用正則表達式匹配任何 port
            pod_pattern = f"{service_type}-{node_name}-.*"
            query = f'completed_requests_per_second{{job="default/pose-podmonitor", pod=~"{pod_pattern}"}}'

        result = await self.query(query)
        
        if result and len(result) > 0:
            # 如果有多個結果，返回第一個的值
            first_result = result[0]
            return float(first_result["value"][1])
        
        return None