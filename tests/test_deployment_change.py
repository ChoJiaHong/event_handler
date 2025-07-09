from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from event_handler import (
    Event,
    Context,
    EventProcessor,
    DeploymentChangeHandler,
    Repository,
    PressureTester,
    ThroughputRecorder,
    AdjustmentCoordinator,
    Dispatcher,
    StateManager,
)


def test_deployment_change_flow():
    async def run():
        repo = Repository()
        tester = PressureTester()
        recorder = ThroughputRecorder()
        adjuster = AdjustmentCoordinator()
        dispatcher = Dispatcher()
        state = StateManager()

        ctx = Context(repo, tester, recorder, adjuster, dispatcher, state)
        processor = EventProcessor(ctx)
        processor.register_handler("DEPLOYMENT_CHANGE", DeploymentChangeHandler())

        event = Event(
            type="DEPLOYMENT_CHANGE",
            payload={"hash": "abc"},
            timestamp=datetime.utcnow(),
            source="detector",
        )

        logging.info("processing deployment change event")
        await processor.process(event)
        logging.info("finished deployment change event")

        assert dispatcher.last_dispatched == 100
        assert await recorder.get("abc") == 100
        assert state.state.value == "stable"

        # Second run should not invoke load test again
        logging.info("processing deployment change event again")
        await processor.process(event)
        logging.info("finished second deployment change event")
        assert dispatcher.last_dispatched == 100

    asyncio.run(run())
