from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from shared.event import Event
from features.throughput.application import Context, register
from features.throughput.infrastructure import (
    InMemoryRepository,
    SimplePressureTester,
    JSONThroughputRepository,
    SimpleAdjustmentStrategy,
    InMemoryDispatcher,
)
from features.throughput.domain.aggregate import StateManager
import event_bus


def test_deployment_change_flow():
    async def run():
        repo = InMemoryRepository()
        tester = SimplePressureTester()
        recorder = JSONThroughputRepository()
        adjuster = SimpleAdjustmentStrategy()
        dispatcher = InMemoryDispatcher()
        state = StateManager()

        ctx = Context(repo, tester, recorder, adjuster, dispatcher, state)
        event_bus.clear()
        register(ctx)

        event = Event(
            type="DEPLOYMENT_CHANGE",
            payload={"hash": {"node": "abc", "services": {}}},
            timestamp=datetime.utcnow(),
            source="detector",
        )

        logging.info("processing deployment change event")
        await event_bus.publish(event)
        logging.info("finished deployment change event")

        assert dispatcher.last_dispatched == 100
        assert await recorder.get({"node": "abc", "services": {}}) == 100
        assert state.state.value == "stable"

        logging.info("processing deployment change event again")
        await event_bus.publish(event)
        logging.info("finished second deployment change event")
        assert dispatcher.last_dispatched == 100

    asyncio.run(run())
