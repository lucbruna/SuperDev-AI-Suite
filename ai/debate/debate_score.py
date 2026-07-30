from __future__ import annotations

from typing import Any


class DebateScore:
    """Calculates and normalizes debate scores."""

    def __init__(self) -> None:
        self._weights: dict[str, float] = {"persuasiveness": 1.0, "logic": 1.0, "evidence": 0.8}

    def set_weight(self, factor: str, weight: float) -> None:
        self._weights[factor] = weight

    async def calculate(self, argument: dict[str, Any]) -> dict[str, Any]:
        raw = argument.get("confidence", 0.5)
        weighted = raw * sum(self._weights.values()) / len(self._weights)
        return {**argument, "score": round(weighted, 2)}

    async def normalize(self, scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not scores:
            return []
        max_score = max(s.get("total_score", 0) for s in scores)
        if max_score == 0:
            return scores
        for s in scores:
            s["normalized"] = round(s.get("total_score", 0) / max_score, 2)
        return scores

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        argument = context.get("argument", {})
        return await self.calculate(argument)
