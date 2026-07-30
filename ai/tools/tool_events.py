from __future__ import annotations

from typing import Any, Callable

EventHandler = Callable[..., Any]


class ToolEvents:
    """Event system for tool lifecycle events."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def on(self, event: str, handler: EventHandler) -> str:
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        return event

    def off(self, event: str, handler: EventHandler) -> bool:
        handlers = self._handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    async def emit(self, event: str, *args: Any, **kwargs: Any) -> list[Any]:
        results: list[Any] = []
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            result = handler(*args, **kwargs)
            if hasattr(result, "__await__"):
                result = await result
            results.append(result)
        return results

    def list_events(self) -> list[str]:
        return list(self._handlers.keys())

    def handler_count(self, event: str) -> int:
        return len(self._handlers.get(event, []))

    @property
    def total_handlers(self) -> int:
        return sum(len(h) for h in self._handlers.values())

    def clear(self) -> None:
        self._handlers.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "events": {e: len(h) for e, h in self._handlers.items()},
            "total_handlers": self.total_handlers,
        }
