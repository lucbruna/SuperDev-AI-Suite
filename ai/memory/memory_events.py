from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from .memory_types import MemoryEventType

EventHandler = Callable[[dict[str, Any]], None]


class MemoryEvents:
    """Event bus for publishing and subscribing to memory events."""

    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}
        self._history: list[dict[str, Any]] = []
        self._max_history: int = 1000

    def subscribe(self, event_type: str | MemoryEventType, handler: EventHandler) -> None:
        key = event_type.name if isinstance(event_type, MemoryEventType) else event_type
        if key not in self._handlers:
            self._handlers[key] = []
        self._handlers[key].append(handler)

    def unsubscribe(self, event_type: str | MemoryEventType, handler: EventHandler) -> bool:
        key = event_type.name if isinstance(event_type, MemoryEventType) else event_type
        if key in self._handlers and handler in self._handlers[key]:
            self._handlers[key].remove(handler)
            return True
        return False

    async def publish(self, event_type: str | MemoryEventType, data: dict[str, Any]) -> None:
        key = event_type.name if isinstance(event_type, MemoryEventType) else event_type
        event = {
            "type": key,
            "data": data,
            "timestamp": time.time(),
        }
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        handlers = self._handlers.get(key, [])
        for handler in handlers:
            handler(event)

    def get_history(self, event_type: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        if event_type:
            key = event_type.name if isinstance(event_type, MemoryEventType) else event_type
            return [e for e in self._history if e["type"] == key][-limit:]
        return list(self._history[-limit:])

    def clear_history(self) -> None:
        self._history.clear()

    @property
    def handler_count(self) -> int:
        return sum(len(h) for h in self._handlers.values())
