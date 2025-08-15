"""Prometheus client for querying metrics via HTTP API."""

from __future__ import annotations

import asyncio
import json
from urllib.parse import urlencode
from urllib.request import urlopen


class PrometheusClient:
    """Retrieve metrics from a Prometheus server."""

    def __init__(self, base_url: str = "http://localhost:9090") -> None:
        self._base = base_url.rstrip("/")

    async def query(self, promql: str) -> dict:
        """Execute a PromQL query and return parsed JSON data."""
        params = urlencode({"query": promql})
        url = f"{self._base}/api/v1/query?{params}"

        def _fetch() -> dict:
            with urlopen(url) as resp:  # nosec - controlled URL
                data = resp.read().decode("utf-8")
            return json.loads(data)

        return await asyncio.to_thread(_fetch)
