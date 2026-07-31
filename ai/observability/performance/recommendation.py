"""Performance recommendations."""

from __future__ import annotations

import time
from typing import Any


class PerformanceRecommendation:
    def __init__(self) -> None:
        self._recommendations: list[dict[str, Any]] = []

    def add(self, category: str, title: str, description: str, priority: str = "medium") -> dict[str, Any]:
        rec = {
            "category": category,
            "title": title,
            "description": description,
            "priority": priority,
            "timestamp": time.time(),
        }
        self._recommendations.append(rec)
        return rec

    def get_by_category(self, category: str) -> list[dict[str, Any]]:
        return [r for r in self._recommendations if r["category"] == category]

    def get_by_priority(self, priority: str) -> list[dict[str, Any]]:
        return [r for r in self._recommendations if r["priority"] == priority]

    def get_all(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._recommendations[-limit:]

    def count(self) -> int:
        return len(self._recommendations)

    def clear(self) -> int:
        n = len(self._recommendations)
        self._recommendations.clear()
        return n
