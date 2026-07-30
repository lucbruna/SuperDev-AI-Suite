from __future__ import annotations

from typing import Any


class Calibration:
    """Calibrates confidence scores to match true accuracy."""

    def __init__(self) -> None:
        self._calibration_data: list[tuple[float, bool]] = []

    async def record(self, confidence: float, correct: bool) -> None:
        self._calibration_data.append((confidence, correct))

    async def calibrate(self, score: float, uncertainty: float = 0.0) -> float:
        adjusted = score * (1 - uncertainty * 0.5)
        return max(0.0, min(1.0, adjusted))

    async def expected_calibration_error(self) -> float:
        if not self._calibration_data:
            return 0.0
        bins: dict[int, list[bool]] = {}
        for conf, correct in self._calibration_data:
            b = int(conf * 10)
            if b not in bins:
                bins[b] = []
            bins[b].append(correct)
        errors: list[float] = []
        for b, outcomes in bins.items():
            avg_confidence = (b + 0.5) / 10
            accuracy = sum(1 for o in outcomes if o) / len(outcomes)
            errors.append(abs(avg_confidence - accuracy))
        return sum(errors) / len(errors) if errors else 0.0

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        score = context.get("score", 0.5)
        uncertainty = context.get("uncertainty", 0.0)
        calibrated = await self.calibrate(score, uncertainty)
        return {"original": score, "calibrated": calibrated}
