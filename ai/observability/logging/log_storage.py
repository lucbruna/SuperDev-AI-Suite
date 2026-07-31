"""Log storage."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class LogStorage:
    def __init__(self, max_entries: int = 100000) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._max = max_entries
    def store(self, entry: Dict[str, Any]) -> bool:
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return True
    def query(self, level: str = "", source: str = "", keyword: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        results = self._entries
        if level:
            results = [e for e in results if e.get("level") == level]
        if source:
            results = [e for e in results if e.get("source") == source]
        if keyword:
            results = [e for e in results if keyword.lower() in str(e.get("message", "")).lower()]
        return results[-limit:]
    def count(self) -> int:
        return len(self._entries)
    def clear(self) -> int:
        n = len(self._entries)
        self._entries.clear()
        return n
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._entries[-limit:]
