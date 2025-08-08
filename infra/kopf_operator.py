"""Kopf-based operator that feeds Kubernetes events into the domain event processor."""

from datetime import datetime
from typing import Any

import kopf

from app.main import build_context, create_processor
from core.domain import Event


class KopfEventBridge:
    """Bridge translating Kopf callbacks into domain events.

    The bridge keeps the event processing logic isolated from Kopf so the
    infrastructure layer can be replaced or extended without touching the
    domain code.  This maintains high cohesion and low coupling in line with
    DDD principles.
    """

    def __init__(self) -> None:
        self._processor = create_processor(build_context())

    async def forward(self, spec: dict[str, Any]) -> None:
        event = Event(
            type=spec.get("type"),
            payload=spec.get("payload", {}),
            timestamp=datetime.utcnow(),
            source="kopf",
        )
        await self._processor.process(event)


_bridge = KopfEventBridge()


@kopf.on.event("example.com", "v1", "events")
async def handle_kopf_event(spec, **_: Any) -> None:
    """Receive custom resources and forward them to the event processor."""
    await _bridge.forward(spec)
