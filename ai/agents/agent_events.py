from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class AgentEvents:
    """Event system for agents."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable]] = {}
        self._history: list[dict[str, Any]] = []

    def on(self, event: str, callback: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable) -> bool:
        listeners = self._listeners.get(event)
        if listeners and callback in listeners:
            listeners.remove(callback)
            return True
        return False

    def emit(self, event: str, data: Any = None) -> None:
        entry = {"event": event, "data": data, "timestamp": time.time()}
        self._history.append(entry)
        for listener in self._listeners.get(event, []):
            listener(data)

    def clear(self) -> None:
        self._listeners.clear()
        self._history.clear()
