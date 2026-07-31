from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable


class FrontendEventType(str, Enum):
    NAVIGATE = "frontend.navigate"
    RENDER = "frontend.render"
    MOUNT = "frontend.mount"
    UNMOUNT = "frontend.unmount"
    STATE_CHANGE = "frontend.state_change"
    ERROR = "frontend.error"
    THEME_CHANGE = "frontend.theme_change"


class FrontendEvents:
    """Emits and subscribes to frontend lifecycle events."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.events")
        self._listeners: dict[str, list[Callable[..., Any]]] = {}

    def emit(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        for listener in list(self._listeners.get(event_type, [])):
            listener(event_type=event_type, payload=payload or {})

    def on(self, event_type: str, listener: Callable[..., Any]) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def off(self, event_type: str, listener: Callable[..., Any]) -> None:
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(listener)
            except ValueError:
                pass

    def once(self, event_type: str, listener: Callable[..., Any]) -> None:
        def _wrapper(**kwargs: Any) -> None:
            self.off(event_type, _wrapper)
            listener(**kwargs)

        self.on(event_type, _wrapper)
