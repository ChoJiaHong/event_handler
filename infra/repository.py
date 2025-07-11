class InMemoryRepository:
    """Simple in-memory repository placeholder."""

    def __init__(self) -> None:
        self.storage = {}

    async def get(self, key):
        return self.storage.get(key)

    async def set(self, key, value):
        self.storage[key] = value
