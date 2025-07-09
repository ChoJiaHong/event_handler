class PressureTester:
    """Stub that 'measures' throughput."""

    async def load_test(self, deployment_hash: str) -> int:
        # In real impl, run load test. Here return fixed value.
        return 100
