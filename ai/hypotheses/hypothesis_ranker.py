from __future__ import annotations

from typing import Any


class HypothesisRanker:
    """Ranks hypotheses by confidence and relevance."""

    def __init__(self) -> None:
        self._weights: dict[str, float] = {"confidence": 1.0, "relevance": 0.5}

    def set_weight(self, factor: str, weight: float) -> None:
        self._weights[factor] = weight

    async def rank(self, hypotheses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        scored = []
        for h in hypotheses:
            score = (
                h.get("confidence", 0) * self._weights.get("confidence", 1)
                + h.get("relevance", 0) * self._weights.get("relevance", 0.5)
            )
            scored.append({**h, "score": score})
        scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        return scored

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        hypotheses = context.get("hypotheses", [])
        ranked = await self.rank(hypotheses)
        return {"ranked": ranked, "count": len(ranked)}
