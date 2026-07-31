"""Event bus: in-memory pub/sub with routing."""

from __future__ import annotations

import time
import uuid
from typing import Any, Callable

from .queue import EventQueue
from .routing import EventRouter


class EventBus:
    """Routes events to subscribers and queues asynchronous deliveries."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict[str, Any]], None]]] = {}
        self.router = EventRouter()
        self.queue = EventQueue()
        self._published: list[dict[str, Any]] = []

    def subscribe(self, event_type: str,
                  handler: Callable[[dict[str, Any]], None]) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: str, payload: dict[str, Any]) -> str:
        event_id = str(uuid.uuid4())
        event: dict[str, Any] = {
            "event_id": event_id,
            "type": event_type,
            "payload": payload,
            "timestamp": time.time(),
        }
        self._published.append(event)
        routes = self.router.route(event_type)
        for target in routes:
            if target not in self._subscribers:
                continue
            for handler in self._subscribers[target]:
                self.queue.enqueue(event, handler)
        return event_id

    def process(self, limit: int = 100) -> int:
        """Processes queued deliveries, returning the number handled."""
        return self.queue.process(limit)

    def published(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._published[-limit:])

    def subscriber_count(self) -> int:
        return sum(len(h) for h in self._subscribers.values())
