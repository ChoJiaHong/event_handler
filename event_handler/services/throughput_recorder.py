class ThroughputRecorder:
    """In-memory store for throughput values."""

    def __init__(self):
        self._values = {}

    async def get(self, deployment_hash: str):
        return self._values.get(deployment_hash)

    async def save(self, deployment_hash: str, throughput: int) -> None:
        self._values[deployment_hash] = throughput
