"""Quality controller — validate and score generated video output."""
from __future__ import annotations

from typing import Any


class QualityController:
    """Runs quality checks on generated videos and produces a score."""

    def __init__(self) -> None:
        self._checks: list[dict[str, Any]] = [
            {"name": "resolution", "weight": 0.3},
            {"name": "temporal_consistency", "weight": 0.3},
            {"name": "audio_sync", "weight": 0.2},
            {"name": "artifact_level", "weight": 0.2},
        ]

    def evaluate(self, result: dict[str, Any]) -> dict[str, Any]:
        """Score a generation result. ``result`` must carry per-check metrics.

        Each check value is expected in [0, 1] where 1 is perfect.
        """
        scores: dict[str, float] = {}
        total_weight = 0.0
        weighted = 0.0
        for check in self._checks:
            name = check["name"]
            raw = result.get(name)
            if raw is None:
                continue
            value = max(0.0, min(1.0, float(raw)))
            scores[name] = value
            weighted += value * check["weight"]
            total_weight += check["weight"]
        overall = weighted / total_weight if total_weight else 0.0
        return {
            "score": round(overall, 3),
            "checks": scores,
            "passed": overall >= result.get("pass_threshold", 0.7),
        }

    def add_check(self, name: str, weight: float) -> None:
        self._checks.append({"name": name, "weight": weight})

    def checks(self) -> list[str]:
        return [c["name"] for c in self._checks]


_quality_controller: QualityController | None = None


def get_quality_controller() -> QualityController:
    global _quality_controller
    if _quality_controller is None:
        _quality_controller = QualityController()
    return _quality_controller
