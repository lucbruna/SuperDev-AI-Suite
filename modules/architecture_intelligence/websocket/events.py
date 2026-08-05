"""Event bus for architecture intelligence (mirrors architecture_graph)."""
from __future__ import annotations

import threading
from collections import deque
from typing import Any, Callable

Listener = Callable[[dict[str, Any]], None]


class EventBus:
    """In-process pub/sub with bounded recent-event log."""

    def __init__(self, keep: int = 100) -> None:
        self._listeners: dict[str, list[Listener]] = {}
        self._recent: deque[dict[str, Any]] = deque(maxlen=keep)
        self._lock = threading.Lock()

    def subscribe(self, event: str, listener: Listener) -> None:
        with self._lock:
            self._listeners.setdefault(event, []).append(listener)

    def publish(self, event: str, payload: dict[str, Any] | None = None) -> None:
        message = {"event": event, "payload": payload or {}}
        with self._lock:
            self._recent.append(message)
            listeners = list(self._listeners.get(event, []))
        for listener in listeners:
            try:
                listener(message)
            except Exception:  # pragma: no cover - defensive
                pass

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._recent)[-limit:]

    def clear(self) -> None:
        with self._lock:
            self._recent.clear()


_bus: EventBus | None = None
_bus_lock = threading.Lock()


def get_bus() -> EventBus:
    global _bus
    if _bus is None:
        with _bus_lock:
            if _bus is None:
                _bus = EventBus()
    return _bus


def publish(event: str, payload: dict[str, Any] | None = None) -> None:
    get_bus().publish(event, payload)
