"""Kopf-based operator that feeds Kubernetes events into the event bus."""

from datetime import datetime
from typing import Any

import kopf

from app.main import build_context
from event_bus import publish, clear
from features.throughput.application.aggregate import register
from shared.event import Event


class KopfEventBridge:
    """Bridge translating Kopf callbacks into domain events."""

    def __init__(self):
        ctx = build_context()
        clear()
        register(ctx)

    async def handle(self, spec: dict, name: str, **_: Any) -> None:
        event = Event(
            type=spec.get("type", ""),
            payload=spec.get("payload", {}),
            timestamp=datetime.utcnow(),
            source=name,
        )
        await publish(event)


bridge = KopfEventBridge()


@kopf.on.create("example.com", "v1", "events")
async def on_create(spec: dict, name: str, **kwargs: Any):
    await bridge.handle(spec, name, **kwargs)
