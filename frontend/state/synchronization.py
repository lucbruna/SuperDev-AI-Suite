from __future__ import annotations

import logging
from typing import Any, Callable

from .state_engine import StateEngine


class StateSynchronization:
    """Synchronizes state across stores and notifies subscribers."""

    def __init__(self, engine: StateEngine | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.state.sync")
        self._engine = engine or StateEngine()
        self._remote: dict[str, Any] = {}
        self._sync_handlers: list[Callable[[str, Any], None]] = []

    @property
    def engine(self) -> StateEngine:
        return self._engine

    def push(self, key: str, value: Any) -> None:
        self._engine.set(key, value)
        self._remote[key] = value
        for handler in self._sync_handlers:
            handler(key, value)

    def pull(self, key: str, default: Any = None) -> Any:
        return self._remote.get(key, default)

    def apply_remote(self, patch: dict[str, Any]) -> None:
        for key, value in patch.items():
            self._engine.set(key, value)
            self._remote[key] = value

    def on_sync(self, handler: Callable[[str, Any], None]) -> None:
        self._sync_handlers.append(handler)

    def diff(self) -> dict[str, Any]:
        return {key: value for key, value in self._remote.items() if self._engine.get(key) != value}

    def reset(self) -> None:
        self._remote.clear()
        self._engine.reset()
