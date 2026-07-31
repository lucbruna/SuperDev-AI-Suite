from __future__ import annotations

from typing import Any


class ConfidenceMetrics:
    """Metrics collection for confidence system."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    async def record(self, prediction: dict[str, Any], actual: Any) -> None:
        self._records.append(
            {
                "predicted_score": prediction.get("score"),
                "actual": actual,
                "confidence": prediction.get("confidence"),
            }
        )

    async def accuracy(self) -> float:
        if not self._records:
            return 0.0
        correct = sum(1 for r in self._records if r.get("predicted_score") == r.get("actual"))
        return correct / len(self._records)

    async def average_confidence(self) -> float:
        if not self._records:
            return 0.0
        confidences = [r.get("confidence", 0) or 0 for r in self._records]
        return sum(confidences) / len(confidences)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "accuracy": await self.accuracy(),
            "avg_confidence": await self.average_confidence(),
            "total": len(self._records),
        }
