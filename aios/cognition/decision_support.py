"""AIOS Decision Support — option scoring and recommendation.

Each option carries weighted criteria; DecisionSupport computes a
weighted score per option and returns a ranked recommendation.
"""

from __future__ import annotations

from typing import Any

Criterion = dict[str, Any]


class DecisionSupport:
    """Rank options by weighted criteria scores."""

    def recommend(self, options: list[dict[str, Any]], criteria: dict[str, float]) -> dict[str, Any]:
        """``options`` items: {"name": str, "scores": {criterion: 0..1}}."""
        scored: list[tuple[float, str, dict[str, Any]]] = []
        for option in options:
            scores = option.get("scores", {})
            total = 0.0
            weight_sum = 0.0
            for criterion, weight in criteria.items():
                weight_sum += abs(weight)
                total += weight * float(scores.get(criterion, 0.0))
            norm = total / weight_sum if weight_sum else 0.0
            scored.append((norm, option.get("name", "?"), option))
        scored.sort(key=lambda pair: -pair[0])
        ranking = [
            {"name": name, "score": round(score, 4), "option": option}
            for score, name, option in scored
        ]
        return {
            "ok": True,
            "ranking": ranking,
            "best": ranking[0] if ranking else None,
            "criteria": criteria,
        }

    def evaluate(self, option: dict[str, Any], criteria: dict[str, float]) -> float:
        result = self.recommend([option], criteria)
        return result["ranking"][0]["score"] if result["ranking"] else 0.0
