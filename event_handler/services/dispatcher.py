class Dispatcher:
    """Send commands to external agents."""

    def __init__(self):
        self.last_dispatched = None

    async def dispatch(self, frequency: int) -> None:
        # Just store the frequency for tests
        self.last_dispatched = frequency
