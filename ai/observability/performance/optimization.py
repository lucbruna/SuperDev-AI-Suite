"""Performance optimization."""
from __future__ import annotations
from typing import Any, Dict, List

class OptimizationRecommender:
    def __init__(self) -> None:
        self._rules: List[Dict[str, Any]] = []
    def add_rule(self, metric: str, threshold: float, recommendation: str, priority: str = "medium") -> None:
        self._rules.append({"metric": metric, "threshold": threshold, "recommendation": recommendation, "priority": priority})
    def analyze(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        recommendations = []
        for rule in self._rules:
            value = metrics.get(rule["metric"], 0)
            if value > rule["threshold"]:
                recommendations.append({"metric": rule["metric"], "current_value": value, "threshold": rule["threshold"], "recommendation": rule["recommendation"], "priority": rule["priority"]})
        return sorted(recommendations, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 4))
    def list_rules(self) -> List[Dict[str, Any]]:
        return list(self._rules)
    def remove_rule(self, index: int) -> bool:
        if 0 <= index < len(self._rules):
            self._rules.pop(index)
            return True
        return False
