"""Application entry point assembling dependencies."""

from core import EventProcessor, Context
from core.domain import Event, StateManager
from handlers import DeploymentChangeHandler, HighLatencyHandler, IdleSystemHandler
from infra import (
    InMemoryRepository,
    SimplePressureTester,
    JSONThroughputRepository,
    InMemoryDispatcher,
    SimpleAdjustmentStrategy,
)


def build_context() -> Context:
    repo = InMemoryRepository()
    tester = SimplePressureTester()
    recorder = JSONThroughputRepository()
    adjuster = SimpleAdjustmentStrategy()
    dispatcher = InMemoryDispatcher()
    state = StateManager()
    return Context(repo, tester, recorder, adjuster, dispatcher, state)


def create_processor(ctx: Context) -> EventProcessor:
    processor = EventProcessor(ctx)
    processor.register_handler("DEPLOYMENT_CHANGE", DeploymentChangeHandler())
    processor.register_handler("HIGH_LATENCY", HighLatencyHandler())
    processor.register_handler("IDLE_SYSTEM", IdleSystemHandler())
    return processor


async def run(event: Event) -> None:
    ctx = build_context()
    processor = create_processor(ctx)
    await processor.process(event)
