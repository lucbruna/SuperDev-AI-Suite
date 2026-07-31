"""Event bus for the Security Engine (Volume 16)."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any


class SecurityEventBus:
    """Minimal in-process pub/sub for security events."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict[str, Any]], Any]]] = {}
        self._history: list[dict[str, Any]] = []
        self._history_limit = 200

    def subscribe(self, event_type: str, handler: Callable[[dict[str, Any]], Any]) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[dict[str, Any]], Any]) -> bool:
        handlers = self._subscribers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    async def emit(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        event = {
            "type": event_type,
            "payload": payload or {},
            "timestamp": __import__("time").time(),
        }
        self._history.append(event)
        if len(self._history) > self._history_limit:
            self._history = self._history[-self._history_limit:]
        for handler in list(self._subscribers.get(event_type, [])):
            result = handler(event)
            if asyncio.iscoroutine(result):
                await result

    def history(self, event_type: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        events = (
            [e for e in self._history if e["type"] == event_type]
            if event_type
            else list(self._history)
        )
        return events[-limit:]

    def snapshot(self) -> dict[str, Any]:
        return {
            "subscribers": {
                event_type: len(handlers)
                for event_type, handlers in self._subscribers.items()
            },
            "events": len(self._history),
        }
