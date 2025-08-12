from domain.services import AdjustmentStrategy

class SimpleAdjustmentStrategy(AdjustmentStrategy):
    """Compute new request frequency."""

    async def compute_frequency(self, throughput: int) -> int:
        return throughput
