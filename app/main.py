"""Application entry point assembling dependencies."""

from features.throughput.application import Context, register
from features.throughput.infrastructure import (
    InMemoryRepository,
    SimplePressureTester,
    JSONThroughputRepository,
    InMemoryDispatcher,
    SimpleAdjustmentStrategy,
)
from features.throughput.domain.aggregate import StateManager
from shared.event import Event
from event_bus import publish, clear
from app.logging_config import setup_logging

# Setup logging when module is imported
setup_logging()


def build_context() -> Context:
    repo = InMemoryRepository()
    tester = SimplePressureTester()
    recorder = JSONThroughputRepository()
    adjuster = SimpleAdjustmentStrategy()
    dispatcher = InMemoryDispatcher()
    state = StateManager()
    return Context(repo, tester, recorder, adjuster, dispatcher, state)


def register_handlers(ctx: Context) -> None:
    clear()
    register(ctx)


async def run(event: Event) -> None:
    ctx = build_context()
    register_handlers(ctx)
    await publish(event)
