from __future__ import annotations

import time
from typing import Any


class StoredEvent:
    """A single stored event."""

    def __init__(self, event_id: str, event_type: str, data: dict[str, Any]):
        self._event_id = event_id
        self._event_type = event_type
        self._data = dict(data)
        self._timestamp = time.time()

    @property
    def event_id(self) -> str:
        return self._event_id

    @property
    def event_type(self) -> str:
        return self._event_type

    @property
    def data(self) -> dict[str, Any]:
        return dict(self._data)

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self._event_id,
            "event_type": self._event_type,
            "data": dict(self._data),
            "timestamp": self._timestamp,
        }


class EventStore:
    """Storage and retrieval of episodic events."""

    def __init__(self):
        self._events: list[StoredEvent] = []
        self._counter: int = 0

    @property
    def count(self) -> int:
        return len(self._events)

    def store(self, event_type: str, data: dict[str, Any]) -> StoredEvent:
        self._counter += 1
        event = StoredEvent(f"evt_{self._counter}", event_type, data)
        self._events.append(event)
        return event

    def get_by_type(self, event_type: str) -> list[StoredEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def get_since(self, timestamp: float) -> list[StoredEvent]:
        return [e for e in self._events if e.timestamp >= timestamp]

    def get_recent(self, count: int = 50) -> list[StoredEvent]:
        return list(self._events[-count:])

    def clear(self) -> None:
        self._events.clear()
