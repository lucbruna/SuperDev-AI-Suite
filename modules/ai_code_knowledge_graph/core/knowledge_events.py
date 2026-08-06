"""Knowledge events — typed event bus for the knowledge pipeline.

Components publish lifecycle events (scan.started, scan.progress, build.done,
error.*) and subscribers react to them. A bounded ring buffer keeps the
recent event history for observability and dashboards.
"""
from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)

EventHandler = Callable[["KnowledgeEvent"], None]


@dataclass(slots=True)
class KnowledgeEvent:
    """A single event published by the knowledge pipeline."""

    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    @property
    def age_seconds(self) -> float:
        return time.time() - self.timestamp


class EventBus:
    """Synchronous pub/sub bus with a recent-event ring buffer."""

    def __init__(self, history_size: int = 500) -> None:
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._wildcard: list[EventHandler] = []
        self._history: deque[KnowledgeEvent] = deque(maxlen=history_size)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        if event_type == "*":
            if handler not in self._wildcard:
                self._wildcard.append(handler)
            return
        self._subscribers.setdefault(event_type, [])
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        if event_type == "*":
            self._wildcard = [h for h in self._wildcard if h is not handler]
            return
        handlers = self._subscribers.get(event_type)
        if handlers:
            self._subscribers[event_type] = [h for h in handlers if h is not handler]

    def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> KnowledgeEvent:
        """Dispatch an event to subscribers and record it in history."""
        event = KnowledgeEvent(type=event_type, payload=payload or {})
        self._history.append(event)
        for handler in list(self._wildcard):
            self._safe_dispatch(handler, event)
        for handler in list(self._subscribers.get(event_type, [])):
            self._safe_dispatch(handler, event)
        return event

    @staticmethod
    def _safe_dispatch(handler: EventHandler, event: KnowledgeEvent) -> None:
        try:
            handler(event)
        except Exception:
            logger.exception("Event handler %r failed for %r", getattr(handler, "__name__", handler), event.type)

    def history(self, limit: int = 50, event_type: str | None = None) -> list[KnowledgeEvent]:
        """Return recent events, newest first, optionally filtered by type."""
        events = list(self._history)
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:][::-1]

    @property
    def history_size(self) -> int:
        return len(self._history)
