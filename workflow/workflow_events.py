from __future__ import annotations

import logging
from typing import Any, Callable


class WorkflowEvents:
    """Event system for workflow lifecycle events."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[dict[str, Any]], None]]] = {}
        self._log = logging.getLogger("superdev.workflow.events")

    def on(self, event: str, handler: Callable[[dict[str, Any]], None]) -> None:
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def off(self, event: str, handler: Callable[[dict[str, Any]], None]) -> None:
        if event in self._handlers:
            self._handlers[event].remove(handler)

    def emit(self, event: str, data: dict[str, Any]) -> None:
        self._log.debug("Event: %s %s", event, data)
        for handler in self._handlers.get(event, []):
            try:
                handler(data)
            except Exception as e:
                self._log.error("Handler error for %s: %s", event, e)
