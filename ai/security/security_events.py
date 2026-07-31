"""Security event bus for cross-cutting security concerns."""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional


class SecurityEvents:
    """Event bus for security-related events across the platform."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[..., Any]]] = {}
        self._event_log: List[Dict[str, Any]] = []

    def on(self, event_type: str, handler: Callable[..., Any]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        entry = {"type": event_type, "data": data, "timestamp": time.time()}
        self._event_log.append(entry)
        for handler in self._handlers.get(event_type, []):
            try:
                handler(data)
            except Exception:
                pass

    def get_log(self, event_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        if event_type:
            entries = [e for e in self._event_log if e["type"] == event_type]
        else:
            entries = self._event_log
        return entries[-limit:]

    def clear_log(self) -> None:
        self._event_log.clear()
