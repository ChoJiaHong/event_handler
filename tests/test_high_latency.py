from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from domain import Event, StateManager
from application import Context, EventProcessor
from application.handlers import HighLatencyHandler
from infrastructure import (
    InMemoryRepository,
    SimplePressureTester,
    JSONThroughputRepository,
    SimpleAdjustmentStrategy,
    InMemoryDispatcher,
)


def test_high_latency_handler_registration():
    called = False

    class CustomHighLatencyHandler(HighLatencyHandler):
        async def handle(self, event: Event, ctx: Context) -> None:
            nonlocal called
            called = True

    async def run():
        repo = InMemoryRepository()
        tester = SimplePressureTester()
        recorder = JSONThroughputRepository()
        adjuster = SimpleAdjustmentStrategy()
        dispatcher = InMemoryDispatcher()
        state = StateManager()
        ctx = Context(repo, tester, recorder, adjuster, dispatcher, state)
        processor = EventProcessor(ctx)
        processor.register_handler("HIGH_LATENCY", CustomHighLatencyHandler())

        event = Event(
            type="HIGH_LATENCY",
            payload={"latency_ms": 500},
            timestamp=datetime.utcnow(),
            source="detector",
        )

        logging.info("processing high latency event")
        await processor.process(event)
        logging.info("finished high latency event")

        assert called
        assert state.state.value == "stable"

    asyncio.run(run())
