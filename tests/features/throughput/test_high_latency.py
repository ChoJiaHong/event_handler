from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from shared.event import Event
from features.throughput.application import Context
from features.throughput.application.handlers.high_latency import HighLatencyHandler
from features.throughput.infrastructure import (
    InMemoryRepository,
    SimplePressureTester,
    JSONThroughputRepository,
    SimpleAdjustmentStrategy,
    InMemoryDispatcher,
)
from features.throughput.domain.aggregate import StateManager
import event_bus


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

        event_bus.clear()

        def wrap(handler):
            async def inner(event: Event):
                entered = await ctx.state.try_enter_adjusting()
                if not entered:
                    return
                try:
                    await handler.handle(event, ctx)
                finally:
                    await ctx.state.exit_adjusting()
            return inner

        event_bus.subscribe("HIGH_LATENCY", wrap(CustomHighLatencyHandler()))

        event = Event(
            type="HIGH_LATENCY",
            payload={"latency_ms": 500},
            timestamp=datetime.utcnow(),
            source="detector",
        )

        logging.info("processing high latency event")
        await event_bus.publish(event)
        logging.info("finished high latency event")

        assert called
        assert state.state.value == "stable"

    asyncio.run(run())
