from __future__ import annotations

import asyncio
from typing import Any, Callable


EventHandler = Callable[..., Any]


class MonitoringEventBus:
    """Async event bus for monitoring-internal pub-sub."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def on(self, event: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def off(self, event: str, handler: EventHandler) -> None:
        self._handlers[event] = [h for h in self._handlers.get(event, []) if h is not handler]

    async def emit(self, event: str, data: dict[str, Any] | None = None) -> None:
        for handler in self._handlers.get(event, []):
            try:
                result = handler(data or {})
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                pass

    def listeners(self, event: str) -> int:
        return len(self._handlers.get(event, []))


__all__ = ["MonitoringEventBus"]
