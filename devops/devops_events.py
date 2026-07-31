from __future__ import annotations

from typing import Any, Callable


class DevOpsEvents:
    """Event system for DevOps lifecycle notifications."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def off(self, event: str, handler: Callable) -> None:
        self._handlers.get(event, []).remove(handler)

    def emit(self, event: str, **data: Any) -> None:
        for handler in self._handlers.get(event, []):
            handler(event=event, data=data)

    def clear(self) -> None:
        self._handlers.clear()
