"""Camera plan — defines camera positions and movements."""
from __future__ import annotations

from typing import Any

MOVES = ["static", "pan", "tilt", "dolly", "crane", "handheld"]


class CameraPlan:
    """Creates a camera plan for the production."""

    def build(self, scenes: int = 1) -> dict[str, Any]:
        return {
            "default_lens": "35mm",
            "moves": MOVES,
            "scene_plan": [{"scene": i + 1, "move": MOVES[i % len(MOVES)]} for i in range(scenes)],
        }


_camera_plan: CameraPlan | None = None


def get_camera_plan() -> CameraPlan:
    global _camera_plan
    if _camera_plan is None:
        _camera_plan = CameraPlan()
    return _camera_plan
