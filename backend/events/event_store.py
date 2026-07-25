from __future__ import annotations

from backend.events.event_bus import Event


class EventStore:
    """In-memory event store."""

    def __init__(self, max_size: int = 10000):
        self._events: list[Event] = []
        self._max_size = max_size

    def append(self, event: Event) -> None:
        self._events.append(event)
        if len(self._events) > self._max_size:
            self._events = self._events[-self._max_size:]

    def get(self, event_id: str) -> Event | None:
        for e in self._events:
            if e.id == event_id:
                return e
        return None

    def list_events(self, event_type: str | None = None, limit: int = 100) -> list[Event]:
        events = self._events
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]

    def clear(self) -> None:
        self._events.clear()
