from datetime import datetime
import asyncio

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
        ctx = Context(repo, tester, recorder, adjuster, dispatcher, state)
        processor = EventProcessor(ctx)
        processor.register_handler("HIGH_LATENCY", CustomHighLatencyHandler())

        event = Event(
            type="HIGH_LATENCY",
            payload={"latency_ms": 500},
            timestamp=datetime.utcnow(),
            source="detector",
        )

        await processor.process(event)

        assert called
        assert state.state.value == "stable"

    asyncio.run(run())
