from ..domain.services import Repository as RepositoryInterface


class InMemoryRepository(RepositoryInterface):
    """Simple in-memory repository placeholder."""

    def __init__(self) -> None:
        self.storage = {}

    async def get(self, key):
        return self.storage.get(key)

    async def set(self, key, value) -> None:
        self.storage[key] = value
