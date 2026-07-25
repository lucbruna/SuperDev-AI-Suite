from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from backend.utils.uuid_utils import generate_uuid


@dataclass
class Event:
    id: str
    type: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    source: str = ""


class EventBus:
    """Simple async event bus."""

    def __init__(self):
        self._handlers: dict[str, list[Callable[..., Awaitable[Any]]]] = {}
        self._history: list[Event] = []

    def subscribe(self, event_type: str, handler: Callable[..., Awaitable[Any]]) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[..., Awaitable[Any]]) -> None:
        if event_type in self._handlers:
            self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler]

    async def publish(self, event_type: str, data: dict[str, Any] | None = None, source: str = "") -> Event:
        event = Event(
            id=generate_uuid(),
            type=event_type,
            data=data or {},
            source=source,
        )
        self._history.append(event)
        for handler in self._handlers.get(event_type, []):
            try:
                await handler(event)
            except Exception:
                pass
        return event

    def get_history(self, event_type: str | None = None, limit: int = 100) -> list[Event]:
        events = self._history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]


event_bus = EventBus()
