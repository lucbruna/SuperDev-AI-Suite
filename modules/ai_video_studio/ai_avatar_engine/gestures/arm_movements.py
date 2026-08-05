"""Arm movements — broad arm gesture vocabulary."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

ARM_GESTURES = [
    Gesture("arm_sweep", 0.7, 0.7, 0.2, "neutral"),
    Gesture("arm_cross", 0.35, 0.35, 0.05, "neutral"),
    Gesture("arm_raise_right", 0.2, 0.9, 0.0, "tilt"),
    Gesture("arm_raise_left", 0.9, 0.2, 0.0, "tilt"),
    Gesture("arm_wide_open", 0.8, 0.8, 0.0, "neutral"),
    Gesture("arm_on_hip", 0.5, 0.1, -0.1, "neutral"),
]


def gestures() -> list[Gesture]:
    return ARM_GESTURES
