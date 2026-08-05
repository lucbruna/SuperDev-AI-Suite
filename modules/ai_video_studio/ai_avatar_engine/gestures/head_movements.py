"""Head movements — head-level gesture vocabulary."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

HEAD_GESTURES = [
    Gesture("head_nod", 0.0, 0.0, 0.0, "nod"),
    Gesture("head_shake", 0.0, 0.0, 0.0, "shake"),
    Gesture("head_tilt_left", 0.0, 0.0, 0.0, "tilt_left"),
    Gesture("head_tilt_right", 0.0, 0.0, 0.0, "tilt_right"),
    Gesture("head_look_up", 0.0, 0.0, 0.0, "up"),
    Gesture("head_look_down", 0.0, 0.0, 0.0, "down"),
]


def gestures() -> list[Gesture]:
    return HEAD_GESTURES
