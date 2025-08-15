from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from shared import Event, StateManager, EventBus
from features.deployment_change import (
    Context,
    DeploymentChangeHandler,
    InMemoryRepository,
    SimplePressureTester,
    JSONThroughputRepository,
    SimpleAdjustmentStrategy,
    InMemoryDispatcher,
)


def test_deployment_change_flow():
    async def run():
        repo = InMemoryRepository()
        tester = SimplePressureTester()
        recorder = JSONThroughputRepository()
        adjuster = SimpleAdjustmentStrategy()
        dispatcher = InMemoryDispatcher()
        state = StateManager()

        ctx = Context(repo, tester, recorder, adjuster, dispatcher, state)
        bus = EventBus(ctx)
        bus.register_handler("DEPLOYMENT_CHANGE", DeploymentChangeHandler())

        event = Event(
            type="DEPLOYMENT_CHANGE",
            payload={"hash": {"node": "abc", "services": {}}},
            timestamp=datetime.utcnow(),
            source="detector",
        )

        logging.info("processing deployment change event")
        await bus.publish(event)
        logging.info("finished deployment change event")

        assert dispatcher.last_dispatched == 100
        assert await recorder.get({"node": "abc", "services": {}}) == 100
        assert state.state.value == "stable"

        logging.info("processing deployment change event again")
        await bus.publish(event)
        logging.info("finished second deployment change event")
        assert dispatcher.last_dispatched == 100

    asyncio.run(run())
