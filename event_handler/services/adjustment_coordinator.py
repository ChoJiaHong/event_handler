class AdjustmentCoordinator:
    """Compute new request frequency."""

    async def compute_frequency(self, throughput: int) -> int:
        # Simple identity mapping for now
        return throughput
