from core.services import PressureTester

class SimplePressureTester(PressureTester):
    """Stub that 'measures' throughput."""

    async def load_test(self, deployment_hash: str) -> int:
        return 100
