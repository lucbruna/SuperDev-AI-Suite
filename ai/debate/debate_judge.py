from __future__ import annotations

from typing import Any


class DebateJudge:
    """Evaluates and scores debate arguments."""

    def __init__(self) -> None:
        self._criteria: dict[str, float] = {
            "logic": 1.0,
            "evidence": 1.0,
            "clarity": 0.8,
            "relevance": 0.9,
        }

    def set_criteria(self, name: str, weight: float) -> None:
        self._criteria[name] = weight

    async def evaluate(self, arguments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        scores = []
        for arg in arguments:
            total = sum(self._criteria.get(c, 0.5) * 0.7 for c in self._criteria)
            scores.append({
                "agent": arg.get("agent"),
                "total_score": round(total / len(self._criteria), 2),
                "confidence": arg.get("confidence", 0),
                "criteria_scores": {c: 0.7 for c in self._criteria},
            })
        scores.sort(key=lambda s: s.get("total_score", 0), reverse=True)
        return scores

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        arguments = context.get("arguments", [])
        return {"scores": await self.evaluate(arguments)}
