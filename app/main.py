"""Application entry point assembling dependencies."""

from shared import Event, StateManager, EventBus
from features.deployment_change import (
    Context,
    DeploymentChangeHandler,
    InMemoryRepository,
    SimplePressureTester,
    JSONThroughputRepository,
    InMemoryDispatcher,
    SimpleAdjustmentStrategy,
)
from features.high_latency import HighLatencyHandler
from features.idle_system import IdleSystemHandler
from app.logging_config import setup_logging

# 在模組載入時設置日誌
setup_logging()


def build_context() -> Context:
    repo = InMemoryRepository()
    tester = SimplePressureTester()
    recorder = JSONThroughputRepository()
    adjuster = SimpleAdjustmentStrategy()
    dispatcher = InMemoryDispatcher()
    state = StateManager()
    return Context(repo, tester, recorder, adjuster, dispatcher, state)


def create_bus(ctx: Context) -> EventBus:
    bus = EventBus(ctx)
    bus.register_handler("DEPLOYMENT_CHANGE", DeploymentChangeHandler())
    bus.register_handler("HIGH_LATENCY", HighLatencyHandler())
    bus.register_handler("IDLE_SYSTEM", IdleSystemHandler())
    return bus


async def run(event: Event) -> None:
    ctx = build_context()
    bus = create_bus(ctx)
    await bus.publish(event)
