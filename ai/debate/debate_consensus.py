from __future__ import annotations

from typing import Any


class DebateConsensus:
    """Reaches consensus from multiple debate arguments."""

    def __init__(self, threshold: float = 0.6):
        self._threshold = threshold

    async def reach(self, arguments: list[dict[str, Any]], scores: list[dict[str, Any]]) -> dict[str, Any]:
        if not arguments or not scores:
            return {"reached": False, "consensus": None}
        avg_confidence = sum(s.get("total_score", 0) for s in scores) / len(scores)
        if avg_confidence >= self._threshold:
            best = scores[0]
            best_arg = next((a for a in arguments if a.get("agent") == best.get("agent")), {})
            return {
                "reached": True,
                "consensus": best_arg.get("points", [""])[0] if best_arg.get("points") else "",
                "confidence": avg_confidence,
                "adopted_from": best.get("agent"),
            }
        return {"reached": False, "consensus": None, "confidence": avg_confidence}

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        arguments = context.get("arguments", [])
        scores = context.get("scores", [])
        return await self.reach(arguments, scores)
