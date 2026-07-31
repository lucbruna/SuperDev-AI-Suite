"""Telemetry: operational events emitted by the integration engine."""

from __future__ import annotations

from typing import Any, Callable


class Telemetry:
    """Collects operational events (started, succeeded, failed)."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []
        self._listeners: list[Callable[[dict[str, Any]], None]] = []

    def emit(self, component: str, event: str,
             details: dict[str, Any] | None = None) -> None:
        entry = {
            "component": component,
            "event": event,
            "details": details or {},
        }
        self._events.append(entry)
        for listener in self._listeners:
            listener(entry)

    def on_event(self, listener: Callable[[dict[str, Any]], None]) -> None:
        self._listeners.append(listener)

    def events(self, component: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        result = self._events
        if component:
            result = [e for e in result if e["component"] == component]
        return list(result[-limit:])

    def failures(self) -> list[dict[str, Any]]:
        return [e for e in self._events if e["event"] == "failed"]
