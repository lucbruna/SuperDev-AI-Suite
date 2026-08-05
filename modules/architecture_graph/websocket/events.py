"""In-process pub/sub bus for graph lifecycle events.

The scheduler and API publish events (build started/finished, refresh, error)
here; the WebSocket endpoint and future integrations subscribe. Kept
dependency-free and thread-safe.
"""
from __future__ import annotations

import threading
import time
import uuid
from collections import deque
from typing import Any, Callable

Subscriber = Callable[[dict[str, Any]], None]


class EventBus:
    """Thread-safe publish/subscribe bus with a bounded recent-event log."""

    def __init__(self, max_log: int = 100) -> None:
        self._lock = threading.Lock()
        self._subscribers: list[Subscriber] = []
        self._log: deque[dict[str, Any]] = deque(maxlen=max_log)

    def subscribe(self, callback: Subscriber) -> Callable[[], None]:
        """Register a subscriber; returns an unsubscribe callable."""
        with self._lock:
            self._subscribers.append(callback)

        def unsubscribe() -> None:
            with self._lock:
                if callback in self._subscribers:
                    self._subscribers.remove(callback)

        return unsubscribe

    def publish(self, event_type: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Publish an event to all subscribers. Never raises."""
        event: dict[str, Any] = {
            "id": uuid.uuid4().hex[:12],
            "type": event_type,
            "ts": time.time(),
            "data": data or {},
        }
        with self._lock:
            subscribers = list(self._subscribers)
            self._log.append(event)
        for callback in subscribers:
            try:
                callback(event)
            except Exception:
                continue  # a bad subscriber must not kill the bus
        return event

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._log)[-limit:]

    def clear(self) -> None:
        with self._lock:
            self._log.clear()


_bus: EventBus | None = None
_bus_lock = threading.Lock()


def get_bus() -> EventBus:
    """Process-wide singleton event bus."""
    global _bus
    if _bus is None:
        with _bus_lock:
            if _bus is None:
                _bus = EventBus()
    return _bus


def publish(event_type: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Convenience publish helper."""
    return get_bus().publish(event_type, data)
