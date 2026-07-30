from __future__ import annotations

from typing import Any

from .confidence_score import ConfidenceScore
from .confidence_threshold import ConfidenceThreshold
from .uncertainty import Uncertainty
from .calibration import Calibration


class ConfidenceEngine:
    """Core confidence estimation engine."""

    def __init__(
        self,
        scorer: ConfidenceScore | None = None,
        threshold: ConfidenceThreshold | None = None,
        uncertainty: Uncertainty | None = None,
        calibration: Calibration | None = None,
    ):
        self._scorer = scorer or ConfidenceScore()
        self._threshold = threshold or ConfidenceThreshold()
        self._uncertainty = uncertainty or Uncertainty()
        self._calibration = calibration or Calibration()

    async def evaluate(self, context: dict[str, Any]) -> dict[str, Any]:
        score = await self._scorer.compute(context)
        uncertainty = await self._uncertainty.estimate(context)
        calibrated = await self._calibration.calibrate(score, uncertainty)
        passed = await self._threshold.check(calibrated)
        return {
            "score": score,
            "uncertainty": uncertainty,
            "calibrated": calibrated,
            "threshold_passed": passed,
        }
