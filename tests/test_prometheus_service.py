import asyncio
from unittest.mock import patch

from event_handler.services.prometheus import PrometheusService


def test_prometheus_query():
    async def run():
        service = PrometheusService("http://localhost:9090")

        def fake_urlopen(url):
            class Resp:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    pass

                def read(self):
                    assert url == "http://localhost:9090/api/v1/query?query=up"
                    return b"{\"status\": \"success\"}"

            return Resp()

        with patch("urllib.request.urlopen", fake_urlopen):
            data = await service.query("up")
            assert data["status"] == "success"

    asyncio.run(run())
