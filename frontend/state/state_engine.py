from __future__ import annotations

import logging
from typing import Any, Callable


class StateEngine:
    """Central state management engine with pub/sub."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.state")
        self._state: dict[str, Any] = {}
        self._listeners: dict[str, list[Callable[[str, Any], None]]] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any, notify: bool = True) -> None:
        self._state[key] = value
        if notify:
            self._emit(key, value)

    def update(self, key: str, **values: Any) -> None:
        current = self._state.get(key, {})
        if isinstance(current, dict):
            merged = {**current, **values}
        else:
            merged = values
        self.set(key, merged)

    def delete(self, key: str) -> bool:
        if key in self._state:
            del self._state[key]
            self._emit(key, None)
            return True
        return False

    def subscribe(self, key: str, listener: Callable[[str, Any], None]) -> None:
        self._listeners.setdefault(key, []).append(listener)

    def unsubscribe(self, key: str, listener: Callable[[str, Any], None]) -> None:
        if key in self._listeners:
            try:
                self._listeners[key].remove(listener)
            except ValueError:
                pass

    def snapshot(self) -> dict[str, Any]:
        return dict(self._state)

    def reset(self) -> None:
        self._state.clear()

    def _emit(self, key: str, value: Any) -> None:
        for listener in list(self._listeners.get(key, [])):
            listener(key, value)
