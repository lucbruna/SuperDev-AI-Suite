"""Digital Twin events."""
from __future__ import annotations
from typing import Any, Callable, Dict, List
import time

class TwinEvents:
    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[..., Any]]] = {}
        self._event_log: List[Dict[str, Any]] = []
    def subscribe(self, event_type: str, handler: Callable[..., Any]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)
    def emit(self, event_type: str, data: Any = None) -> None:
        self._event_log.append({"type": event_type, "data": data, "timestamp": time.time()})
        for handler in self._handlers.get(event_type, []):
            try:
                handler(data)
            except Exception:
                pass
    def get_log(self, event_type: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        log = self._event_log
        if event_type:
            log = [e for e in log if e["type"] == event_type]
        return log[-limit:]
    def clear_log(self) -> int:
        n = len(self._event_log)
        self._event_log.clear()
        return n
    def handler_count(self, event_type: str = "") -> int:
        if event_type:
            return len(self._handlers.get(event_type, []))
        return sum(len(v) for v in self._handlers.values())
