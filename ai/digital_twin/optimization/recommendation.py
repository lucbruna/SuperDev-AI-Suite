"""Recommendation engine."""
from __future__ import annotations
from typing import Any, Dict, List

class RecommendationEngine:
    def __init__(self) -> None:
        self._recommendations: List[Dict[str, Any]] = []
    def generate(self, context: Dict[str, Any], rules: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        rules = rules or [{"condition": "default", "action": "maintain", "priority": 1}]
        recs = []
        for rule in rules:
            recs.append({"action": rule.get("action", ""), "priority": rule.get("priority", 1), "confidence": 0.8})
        result = {"context": context, "recommendations": recs, "count": len(recs)}
        self._recommendations.append(result)
        return result
    def prioritize(self, recommendations: List[Dict[str, Any]], metric: str = "priority") -> List[Dict[str, Any]]:
        return sorted(recommendations, key=lambda r: r.get(metric, 0), reverse=True)
    def get_recommendations(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._recommendations[-limit:]
    def count(self) -> int:
        return len(self._recommendations)
    def clear(self) -> int:
        n = len(self._recommendations)
        self._recommendations.clear()
        return n
