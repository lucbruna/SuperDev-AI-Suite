"""Lips controller — lip shape/rounding/pressure deltas."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp


class LipsController:
    """Produces lip-shape parameters."""

    def drive(self, *, round: float = 0.0, pressed: float = 0.0, width: float = 0.0) -> dict[str, Any]:
        return {
            "mouth_round": clamp(round, -1.0, 1.0),
            "lips_pressed": clamp(pressed, -1.0, 1.0),
            "mouth_width": clamp(width, -1.0, 1.0),
        }


_lips_controller: LipsController | None = None


def get_lips_controller() -> LipsController:
    global _lips_controller
    if _lips_controller is None:
        _lips_controller = LipsController()
    return _lips_controller
