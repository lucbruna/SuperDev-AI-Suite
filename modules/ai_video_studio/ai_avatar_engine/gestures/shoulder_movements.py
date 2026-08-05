"""Shoulder movements — shoulder-level gesture vocabulary."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

SHOULDER_GESTURES = [
    Gesture("shoulder_shrug", 0.5, 0.5, -0.2, "neutral"),
    Gesture("shoulder_roll", 0.4, 0.4, 0.1, "neutral"),
    Gesture("shoulder_back", 0.2, 0.2, 0.0, "neutral"),
]


def gestures() -> list[Gesture]:
    return SHOULDER_GESTURES
