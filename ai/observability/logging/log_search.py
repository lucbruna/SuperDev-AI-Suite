"""Log search."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class LogSearch:
    def __init__(self, storage: Any = None) -> None:
        self._storage = storage
        self._search_history: List[Dict[str, Any]] = []
    def search(self, query: str, level: str = "", source: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        start = time.time()
        if self._storage and hasattr(self._storage, 'query'):
            results = self._storage.query(level=level, source=source, keyword=query, limit=limit)
        else:
            results = []
        elapsed = time.time() - start
        self._search_history.append({"query": query, "results": len(results), "time": elapsed})
        return results
    def search_by_time(self, start_time: float, end_time: float, level: str = "") -> List[Dict[str, Any]]:
        if self._storage and hasattr(self._storage, 'query'):
            all_entries = self._storage.query(level=level, limit=10000)
            return [e for e in all_entries if start_time <= e.get("timestamp", 0) <= end_time]
        return []
    def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._search_history[-limit:]
