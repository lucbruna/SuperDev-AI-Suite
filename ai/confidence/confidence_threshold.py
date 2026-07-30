from __future__ import annotations

from typing import Any


class ConfidenceThreshold:
    """Manages confidence thresholds for decision gates."""

    def __init__(self, threshold: float = 0.7):
        self._threshold = threshold
        self._dynamic_thresholds: dict[str, float] = {}

    def set_threshold(self, threshold: float) -> None:
        self._threshold = max(0.0, min(1.0, threshold))

    def set_dynamic_threshold(self, context_type: str, threshold: float) -> None:
        self._dynamic_thresholds[context_type] = max(0.0, min(1.0, threshold))

    async def check(self, score: float, context_type: str | None = None) -> bool:
        threshold = self._dynamic_thresholds.get(context_type, self._threshold) if context_type else self._threshold
        return score >= threshold

    async def evaluate(self, context: dict[str, Any]) -> dict[str, Any]:
        score = context.get("score", 0.0)
        context_type = context.get("context_type")
        passed = await self.check(score, context_type)
        threshold = self._dynamic_thresholds.get(context_type, self._threshold) if context_type else self._threshold
        return {"score": score, "passed": passed, "threshold": threshold}
