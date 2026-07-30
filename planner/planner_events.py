from __future__ import annotations

from typing import Any, Callable

Listener = Callable[[str, dict[str, Any]], None]


class PlannerEvents:
    """Event system for the planner module."""

    def __init__(self):
        self._listeners: dict[str, list[Listener]] = {}

    def on(self, event: str, listener: Listener) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(listener)

    def off(self, event: str, listener: Listener) -> None:
        if event in self._listeners:
            self._listeners[event] = [l for l in self._listeners[event] if l is not listener]

    def emit(self, event: str, data: dict[str, Any] | None = None) -> None:
        for listener in self._listeners.get(event, []):
            try:
                listener(event, data or {})
            except Exception:
                pass
