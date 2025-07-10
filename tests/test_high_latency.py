from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from event_handler import (
    Event,
    Context,
    EventProcessor,
    HighLatencyHandler,
    Repository,
    PressureTester,
    ThroughputRecorder,
    AdjustmentCoordinator,
    Dispatcher,
    StateManager,
    PrometheusService,
)


def test_high_latency_handler_registration():
    called = False

    class CustomHighLatencyHandler(HighLatencyHandler):
        async def handle(self, event: Event, ctx: Context) -> None:
            nonlocal called
            called = True

    async def run():
        repo = Repository()
        tester = PressureTester()
        recorder = ThroughputRecorder()
        adjuster = AdjustmentCoordinator()
        dispatcher = Dispatcher()
        state = StateManager()
        prometheus = PrometheusService("http://localhost:9090")
        ctx = Context(repo, tester, recorder, adjuster, dispatcher, state, prometheus)
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
