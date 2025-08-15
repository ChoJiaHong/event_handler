import asyncio
import json
from unittest.mock import patch

from infra import PrometheusClient


class DummyResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_prometheus_query():
    async def run():
        client = PrometheusClient("http://prom:9090")
        data = {"status": "success", "data": {"result": []}}
        payload = json.dumps(data).encode("utf-8")
        with patch("infra.prometheus_client.urlopen") as mock_urlopen:
            mock_urlopen.return_value = DummyResponse(payload)
            result = await client.query("up")
            assert result == data
            called_url = mock_urlopen.call_args.args[0]
            assert called_url.startswith("http://prom:9090/api/v1/query?")
            assert "query=up" in called_url

    asyncio.run(run())
