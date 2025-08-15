from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from shared import Event, StateManager, EventBus
from features.deployment_change import (
    Context,
    InMemoryRepository,
    SimplePressureTester,
    JSONThroughputRepository,
    SimpleAdjustmentStrategy,
    InMemoryDispatcher,
)
from features.high_latency import HighLatencyHandler


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
        bus = EventBus(ctx)
        bus.register_handler("HIGH_LATENCY", CustomHighLatencyHandler())

        event = Event(
            type="HIGH_LATENCY",
            payload={"latency_ms": 500},
            timestamp=datetime.utcnow(),
            source="detector",
        )

        logging.info("processing high latency event")
        await bus.publish(event)
        logging.info("finished high latency event")

        assert called
        assert state.state.value == "stable"

    asyncio.run(run())
