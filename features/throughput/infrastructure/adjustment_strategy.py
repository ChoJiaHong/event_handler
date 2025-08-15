from features.throughput.domain.services.adjustment_strategy import AdjustmentStrategy

class SimpleAdjustmentStrategy(AdjustmentStrategy):
    """Compute new request frequency."""

    async def compute_frequency(self, throughput: int) -> int:
        return throughput
