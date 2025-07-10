import asyncio
import json
from urllib import parse, request


class PrometheusService:
    """Simple client for Prometheus HTTP API."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def query(self, query: str) -> dict:
        """Run an instant query and return the JSON response."""

        def _fetch() -> dict:
            url = f"{self.base_url}/api/v1/query?query={parse.quote(query)}"
            with request.urlopen(url) as resp:
                return json.loads(resp.read().decode())

        return await asyncio.to_thread(_fetch)
