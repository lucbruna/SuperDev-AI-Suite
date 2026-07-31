from __future__ import annotations

from typing import Any


class HypothesisMetrics:
    """Metrics collection for hypothesis generation."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    async def record(self, operation: str, hypothesis: dict[str, Any]) -> None:
        self._records.append(
            {
                "operation": operation,
                "hypothesis_id": hypothesis.get("id"),
                "confidence": hypothesis.get("confidence"),
            }
        )

    async def average_confidence(self) -> float:
        if not self._records:
            return 0.0
        confidences = [r.get("confidence", 0) or 0 for r in self._records]
        return sum(confidences) / len(confidences)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return {"total_operations": len(self._records), "avg_confidence": await self.average_confidence()}
