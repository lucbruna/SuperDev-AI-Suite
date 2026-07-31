"""Enterprise event bus."""
from __future__ import annotations

import contextlib
import time
from collections.abc import Callable
from typing import Any


class EnterpriseEvents:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[..., Any]]] = {}
        self._event_log: list[dict[str, Any]] = []
    def subscribe(self, event_type: str, handler: Callable[..., Any]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)
    def unsubscribe(self, event_type: str, handler: Callable[..., Any]) -> bool:
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False
    def emit(self, event_type: str, data: Any = None) -> None:
        self._event_log.append({"type": event_type, "data": data, "timestamp": time.time()})
        for handler in self._handlers.get(event_type, []):
            with contextlib.suppress(Exception):
                handler(data)
    def get_log(self, event_type: str = "", limit: int = 100) -> list[dict[str, Any]]:
        log = self._event_log
        if event_type:
            log = [e for e in log if e["type"] == event_type]
        return log[-limit:]
    def clear_log(self) -> int:
        n = len(self._event_log)
        self._event_log.clear()
        return n
