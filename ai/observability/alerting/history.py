"""Alert history."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class AlertHistory:
    def __init__(self, max_entries: int = 1000) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._max = max_entries
    def record(self, alert: Dict[str, Any], action: str = "created") -> Dict[str, Any]:
        entry = {"alert": alert, "action": action, "timestamp": time.time()}
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return entry
    def query(self, alert_type: str = "", action: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        results = self._entries
        if alert_type:
            results = [e for e in results if e.get("alert", {}).get("type") == alert_type]
        if action:
            results = [e for e in results if e["action"] == action]
        return results[-limit:]
    def count(self) -> int:
        return len(self._entries)
    def clear(self) -> int:
        n = len(self._entries)
        self._entries.clear()
        return n
    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._entries[-limit:]
