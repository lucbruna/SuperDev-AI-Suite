from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from backend.events.event_bus import event_bus


class EventListener:
    """Event listener helper."""

    def __init__(self):
        self._subscriptions: list[tuple[str, Callable]] = []

    def on(self, event_type: str, handler: Callable[..., Awaitable[Any]]) -> None:
        event_bus.subscribe(event_type, handler)
        self._subscriptions.append((event_type, handler))

    def unsubscribe_all(self) -> None:
        for event_type, handler in self._subscriptions:
            event_bus.unsubscribe(event_type, handler)
        self._subscriptions.clear()
