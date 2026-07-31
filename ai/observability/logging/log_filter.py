"""Log filters."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


class LogFilter:
    def __init__(self) -> None:
        self._filters: dict[str, Callable[[dict[str, Any]], bool]] = {}
    def add_level_filter(self, min_level: str = "info") -> None:
        levels = ["debug", "info", "warning", "error", "critical"]
        min_idx = levels.index(min_level) if min_level in levels else 1
        def filt(e: dict[str, Any]) -> bool:
            return levels.index(e.get("level", "info")) >= min_idx
        self._filters["level"] = filt
    def add_source_filter(self, allowed_sources: list[str]) -> None:
        def filt(e: dict[str, Any]) -> bool:
            return e.get("source", "") in allowed_sources
        self._filters["source"] = filt
    def add_keyword_filter(self, keywords: list[str]) -> None:
        def filt(e: dict[str, Any]) -> bool:
            msg = str(e.get("message", "")).lower()
            return any(kw.lower() in msg for kw in keywords)
        self._filters["keyword"] = filt
    def apply(self, entry: dict[str, Any]) -> bool:
        return all(f(entry) for f in self._filters.values())
    def apply_batch(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [e for e in entries if self.apply(e)]
    def list_filters(self) -> list[str]:
        return list(self._filters.keys())
    def remove_filter(self, name: str) -> bool:
        if name in self._filters:
            del self._filters[name]
            return True
        return False
