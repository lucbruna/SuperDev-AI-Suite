"""Pointing — directional pointing gestures."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

POINTING_GESTURES = [
    Gesture("point_forward", 0.85, 0.3, 0.15, "tilt"),
    Gesture("point_left", 0.9, 0.2, 0.0, "tilt_left"),
    Gesture("point_right", 0.2, 0.9, 0.0, "tilt_right"),
    Gesture("point_up", 0.9, 0.9, -0.1, "up"),
    Gesture("point_self", 0.4, 0.2, 0.0, "down"),
]


def gestures() -> list[Gesture]:
    return POINTING_GESTURES
