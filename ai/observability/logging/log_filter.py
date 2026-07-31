"""Log filters."""
from __future__ import annotations
from typing import Any, Callable, Dict, List

class LogFilter:
    def __init__(self) -> None:
        self._filters: Dict[str, Callable[[Dict[str, Any]], bool]] = {}
    def add_level_filter(self, min_level: str = "info") -> None:
        levels = ["debug", "info", "warning", "error", "critical"]
        min_idx = levels.index(min_level) if min_level in levels else 1
        def filt(e: Dict[str, Any]) -> bool:
            return levels.index(e.get("level", "info")) >= min_idx
        self._filters["level"] = filt
    def add_source_filter(self, allowed_sources: List[str]) -> None:
        def filt(e: Dict[str, Any]) -> bool:
            return e.get("source", "") in allowed_sources
        self._filters["source"] = filt
    def add_keyword_filter(self, keywords: List[str]) -> None:
        def filt(e: Dict[str, Any]) -> bool:
            msg = str(e.get("message", "")).lower()
            return any(kw.lower() in msg for kw in keywords)
        self._filters["keyword"] = filt
    def apply(self, entry: Dict[str, Any]) -> bool:
        return all(f(entry) for f in self._filters.values())
    def apply_batch(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [e for e in entries if self.apply(e)]
    def list_filters(self) -> List[str]:
        return list(self._filters.keys())
    def remove_filter(self, name: str) -> bool:
        if name in self._filters:
            del self._filters[name]
            return True
        return False
