from typing import Awaitable, Callable, Dict, List
from shared.event import Event

_subscribers: Dict[str, List[Callable[[Event], Awaitable[None]]]] = {}


def subscribe(event_type: str, handler: Callable[[Event], Awaitable[None]]) -> None:
    _subscribers.setdefault(event_type, []).append(handler)


def clear() -> None:
    _subscribers.clear()


def get_subscribers() -> Dict[str, List[Callable[[Event], Awaitable[None]]]]:
    return _subscribers


async def publish(event: Event) -> None:
    for handler in _subscribers.get(event.type, []):
        await handler(event)

__all__ = ["subscribe", "publish", "clear", "get_subscribers"]
