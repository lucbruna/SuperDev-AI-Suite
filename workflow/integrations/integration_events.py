from __future__ import annotations

import logging
from typing import Any, Callable


class IntegrationEvents:
    """Event bus for integration lifecycle events."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[..., Any]]] = {}
        self._log = logging.getLogger("superdev.workflow.integrations.events")

    def on(self, event: str, listener: Callable[..., Any]) -> None:
        self._listeners.setdefault(event, []).append(listener)

    def emit(self, event: str, **data: Any) -> None:
        for listener in self._listeners.get(event, []):
            listener(**data)
