"""Performance recommendations."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class PerformanceRecommendation:
    def __init__(self) -> None:
        self._recommendations: List[Dict[str, Any]] = []
    def add(self, category: str, title: str, description: str, priority: str = "medium") -> Dict[str, Any]:
        rec = {"category": category, "title": title, "description": description, "priority": priority, "timestamp": time.time()}
        self._recommendations.append(rec)
        return rec
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        return [r for r in self._recommendations if r["category"] == category]
    def get_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        return [r for r in self._recommendations if r["priority"] == priority]
    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._recommendations[-limit:]
    def count(self) -> int:
        return len(self._recommendations)
    def clear(self) -> int:
        n = len(self._recommendations)
        self._recommendations.clear()
        return n
