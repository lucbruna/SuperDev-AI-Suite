from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class RecentEvent:
    """A single recent event."""

    def __init__(self, event_type: str, data: Dict[str, Any]):
        self._type = event_type
        self._data = dict(data)
        self._timestamp = time.time()

    @property
    def event_type(self) -> str:
        return self._type

    @property
    def data(self) -> Dict[str, Any]:
        return dict(self._data)

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self._type,
            "data": dict(self._data),
            "timestamp": self._timestamp,
        }


class RecentEvents:
    """Ring buffer of recent events."""

    def __init__(self, max_events: int = 500):
        self._max_events = max_events
        self._events: List[RecentEvent] = []

    @property
    def max_events(self) -> int:
        return self._max_events

    @property
    def count(self) -> int:
        return len(self._events)

    def record(self, event_type: str, data: Dict[str, Any]) -> None:
        event = RecentEvent(event_type, data)
        self._events.append(event)
        if len(self._events) > self._max_events:
            self._events.pop(0)

    def get_recent(self, count: int = 10) -> List[RecentEvent]:
        return list(self._events[-count:])

    def get_by_type(self, event_type: str) -> List[RecentEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def get_since(self, timestamp: float) -> List[RecentEvent]:
        return [e for e in self._events if e.timestamp >= timestamp]

    def clear(self) -> None:
        self._events.clear()

    def to_dict_list(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._events]
