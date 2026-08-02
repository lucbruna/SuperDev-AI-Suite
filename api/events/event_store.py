from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any

from ..api_logger import APILogger
from .event_bus import Event


class EventStore:
    """In-memory event store for auditing, replay, and inspection."""

    def __init__(self, max_events: int = 10000, logger: APILogger | None = None) -> None:
        self._events: list[Event] = []
        self._max_events = max_events
        self._index_by_topic: dict[str, list[int]] = {}
        self._logger = logger or APILogger(__name__)

    def append(self, event: Event) -> None:
        self._events.append(event)
        idx = len(self._events) - 1
        self._index_by_topic.setdefault(event.topic, []).append(idx)
        if len(self._events) > self._max_events:
            self._trim()

    def _trim(self) -> None:
        excess = len(self._events) - self._max_events
        removed = self._events[:excess]
        self._events = self._events[excess:]
        # Rebuild topic index
        self._index_by_topic.clear()
        for idx, evt in enumerate(self._events):
            self._index_by_topic.setdefault(evt.topic, []).append(idx)
        self._logger.debug(f"Trimmed {excess} events from store")

    def get_all(self) -> Sequence[Event]:
        return list(self._events)

    def get_by_topic(self, topic: str) -> Sequence[Event]:
        indices = self._index_by_topic.get(topic, [])
        return [self._events[i] for i in indices if i < len(self._events)]

    def get_by_id(self, event_id: str) -> Event | None:
        for event in reversed(self._events):
            if event.id == event_id:
                return event
        return None

    def get_recent(self, count: int = 10) -> Sequence[Event]:
        return list(self._events[-count:])

    def search(self, *, topic: str | None = None, source: str | None = None, **metadata: Any) -> Sequence[Event]:
        results: list[Event] = []
        for event in self._events:
            if topic and event.topic != topic:
                continue
            if source and event.source != source:
                continue
            if metadata and not all(event.metadata.get(k) == v for k, v in metadata.items()):
                continue
            results.append(event)
        return results

    def count(self) -> int:
        return len(self._events)

    def clear(self) -> None:
        self._events.clear()
        self._index_by_topic.clear()

    def replay(self, topic: str | None = None) -> Sequence[Event]:
        if topic:
            return self.get_by_topic(topic)
        return self.get_all()

    def since(self, timestamp: float) -> Sequence[Event]:
        return [e for e in self._events if e.timestamp > timestamp]

    def between(self, start: float, end: float) -> Sequence[Event]:
        return [e for e in self._events if start <= e.timestamp <= end]
