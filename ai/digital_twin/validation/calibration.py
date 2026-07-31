"""Calibration validation."""
from __future__ import annotations

from typing import Any


class CalibrationValidator:
    def __init__(self) -> None:
        self._calibrations: list[dict[str, Any]] = []
    def validate(self, model_confidence: list[float], actual_accuracy: list[float]) -> dict[str, Any]:
        if len(model_confidence) != len(actual_accuracy):
            return {"error": "mismatched_lengths"}
        n = len(model_confidence)
        avg_confidence = sum(model_confidence) / n if n > 0 else 0
        avg_accuracy = sum(actual_accuracy) / n if n > 0 else 0
        calibration_error = abs(avg_confidence - avg_accuracy)
        well_calibrated = calibration_error < 0.05
        result = {"calibration_error": calibration_error, "avg_confidence": avg_confidence, "avg_accuracy": avg_accuracy, "well_calibrated": well_calibrated, "samples": n}
        self._calibrations.append(result)
        return result
    def expected_calibration_error(self, confidences: list[float], accuracies: list[float], n_bins: int = 10) -> float:
        if not confidences:
            return 0.0
        bins = [[] for _ in range(n_bins)]
        for conf, acc in zip(confidences, accuracies, strict=False):
            bin_idx = min(int(conf * n_bins), n_bins - 1)
            bins[bin_idx].append((conf, acc))
        ece = 0.0
        total = len(confidences)
        for bin_items in bins:
            if bin_items:
                bin_acc = sum(a for _, a in bin_items) / len(bin_items)
                bin_conf = sum(c for c, _ in bin_items) / len(bin_items)
                ece += len(bin_items) / total * abs(bin_acc - bin_conf)
        return ece
    def get_calibrations(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._calibrations[-limit:]
    def count(self) -> int:
        return len(self._calibrations)
