from __future__ import annotations

import logging
from typing import Any, Callable


class CodeEvents:
    """Event bus for code lifecycle events."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[..., Any]]] = {}
        self._log = logging.getLogger("superdev.code.events")

    def on(self, event: str, listener: Callable[..., Any]) -> None:
        self._listeners.setdefault(event, []).append(listener)

    def emit(self, event: str, **data: Any) -> None:
        self._log.debug("Code event: %s", event)
        for listener in self._listeners.get(event, []):
            listener(**data)
