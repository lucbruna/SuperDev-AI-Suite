"""Scene optimizer — optimize scene pacing and density."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError

TARGET_RANGE = (2.0, 12.0)


class SceneOptimizer:
    """Optimizes scene durations and pacing heuristics."""

    def optimize_durations(self, scenes: list[dict[str, Any]], target_total: float) -> dict[str, Any]:
        if not scenes:
            raise ValidationError("No scenes to optimize", field="scenes")
        if target_total <= 0:
            raise ValidationError("target_total must be positive", field="target_total")

        current = sum(s.get("duration", 0) for s in scenes)
        if current <= 0:
            per_scene = target_total / len(scenes)
            for s in scenes:
                s["duration"] = round(per_scene, 3)
        else:
            scale = target_total / current
            for s in scenes:
                s["duration"] = round(s.get("duration", 0) * scale, 3)

        return {
            "target_total": target_total,
            "actual_total": round(sum(s["duration"] for s in scenes), 3),
            "scene_count": len(scenes),
        }

    def flag_outliers(self, scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Flag scenes whose duration is outside a healthy range."""
        flags: list[dict[str, Any]] = []
        for i, s in enumerate(scenes):
            duration = s.get("duration", 0)
            if duration < TARGET_RANGE[0]:
                flags.append({"index": i, "issue": "too_short", "duration": duration})
            elif duration > TARGET_RANGE[1]:
                flags.append({"index": i, "issue": "too_long", "duration": duration})
        return flags

    def rebalance(self, scenes: list[dict[str, Any]], target_total: float) -> dict[str, Any]:
        result = self.optimize_durations(scenes, target_total)
        result["flags"] = self.flag_outliers(scenes)
        return result


_scene_optimizer: SceneOptimizer | None = None


def get_scene_optimizer() -> SceneOptimizer:
    global _scene_optimizer
    if _scene_optimizer is None:
        _scene_optimizer = SceneOptimizer()
    return _scene_optimizer
