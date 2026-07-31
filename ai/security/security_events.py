"""Security event bus for cross-cutting security concerns."""
from __future__ import annotations

import contextlib
import time
from collections.abc import Callable
from typing import Any


class SecurityEvents:
    """Event bus for security-related events across the platform."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[..., Any]]] = {}
        self._event_log: list[dict[str, Any]] = []

    def on(self, event_type: str, handler: Callable[..., Any]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(self, event_type: str, data: dict[str, Any]) -> None:
        entry = {"type": event_type, "data": data, "timestamp": time.time()}
        self._event_log.append(entry)
        for handler in self._handlers.get(event_type, []):
            with contextlib.suppress(Exception):
                handler(data)

    def get_log(self, event_type: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        entries = [e for e in self._event_log if e["type"] == event_type] if event_type else self._event_log
        return entries[-limit:]

    def clear_log(self) -> None:
        self._event_log.clear()
