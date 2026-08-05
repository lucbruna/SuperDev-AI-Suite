"""Gaze controller — combines eye tracking, contact and head tilt."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.facial_animation.eye_contact import (
    get_eye_contact,
)
from modules.ai_video_studio.ai_avatar_engine.facial_animation.eye_tracking import (
    get_eye_tracking,
)
from modules.ai_video_studio.editor_common import clamp


class GazeController:
    """Produces final gaze + head-tilt parameters."""

    def drive(self, *, t: float = 0.0, target_x: float = 0.0,
              target_y: float = 0.0) -> dict[str, Any]:
        tracking = get_eye_tracking().track(target_x=target_x, target_y=target_y)
        contact = get_eye_contact().drive(t=t)
        gaze_x = clamp(tracking["gaze_x"] + contact.get("gaze_x", 0.0), -1.0, 1.0)
        gaze_y = clamp(tracking["gaze_y"] + contact.get("gaze_y", 0.0), -1.0, 1.0)
        return {
            "gaze_x": round(gaze_x, 3),
            "gaze_y": round(gaze_y, 3),
            "head_tilt": round(-gaze_x * 6.0, 3),
            "contact": contact.get("contact", 1.0),
        }


_gaze_controller: GazeController | None = None


def get_gaze_controller() -> GazeController:
    global _gaze_controller
    if _gaze_controller is None:
        _gaze_controller = GazeController()
    return _gaze_controller
