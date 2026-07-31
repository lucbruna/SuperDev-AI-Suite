"""Meta-learning engine for learning how to learn."""
from __future__ import annotations

from typing import Any, Dict, List


class MetaLearner:
    """Analyzes learning patterns to improve learning strategies."""

    def __init__(self) -> None:
        self._meta_strategies: Dict[str, float] = {
            "few_shot": 0.6,
            "pattern_recognition": 0.7,
            "analogical_reasoning": 0.65,
            "incremental_refinement": 0.8,
        }

    def analyze(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not experiences:
            return {"strategy_scores": dict(self._meta_strategies), "recommendation": "Collect more data"}
        issue_counts: Dict[str, int] = {}
        for exp in experiences:
            issue = exp.get("issue", "unknown")
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        most_common = max(issue_counts, key=issue_counts.get) if issue_counts else "none"
        return {
            "strategy_scores": dict(self._meta_strategies),
            "most_common_issue": most_common,
            "total_experiences": len(experiences),
            "recommendation": self._recommend_strategy(most_common),
        }

    def _recommend_strategy(self, issue_type: str) -> str:
        mapping = {
            "performance_drop": "Use incremental_refinement strategy",
            "error_increase": "Apply pattern_recognition to catch error patterns",
            "slow_response": "Use few_shot learning to optimize critical paths",
            "low_quality": "Apply analogical_reasoning from high-quality examples",
        }
        return mapping.get(issue_type, "General review recommended")

    def update_strategy(self, strategy: str, score: float) -> None:
        if strategy in self._meta_strategies:
            self._meta_strategies[strategy] = round(min(max(score, 0.0), 1.0), 2)
