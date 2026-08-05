"""Camera planner — suggest camera setups and movements per scene."""
from __future__ import annotations

from typing import Any

CAMERA_PRESETS = {
    "wide": {"lens": "24mm", "movement": "static", "notes": "Establishes the environment"},
    "medium": {"lens": "50mm", "movement": "subtle pan", "notes": "Balanced subject framing"},
    "close_up": {"lens": "85mm", "movement": "slight tilt", "notes": "Captures emotion and detail"},
    "aerial": {"lens": "18mm", "movement": "orbit", "notes": "Top-down establishing shot"},
    "tracking": {"lens": "35mm", "movement": "track", "notes": "Follows the subject"},
}


class CameraPlanner:
    """Deterministic camera plan generation per scene/shot."""

    def plan(self, shot_type: str = "medium") -> dict[str, Any]:
        preset = CAMERA_PRESETS.get(shot_type, CAMERA_PRESETS["medium"])
        return {
            "shot_type": shot_type,
            "lens": preset["lens"],
            "movement": preset["movement"],
            "height": "eye level",
            "angle": "neutral",
            "notes": preset["notes"],
        }

    def plan_sequence(self, shot_types: list[str]) -> list[dict[str, Any]]:
        return [self.plan(s) for s in shot_types]

    def list_presets(self) -> list[str]:
        return list(CAMERA_PRESETS.keys())


_camera_planner: CameraPlanner | None = None


def get_camera_planner() -> CameraPlanner:
    global _camera_planner
    if _camera_planner is None:
        _camera_planner = CameraPlanner()
    return _camera_planner
