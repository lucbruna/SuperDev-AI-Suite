"""Hand movements — expressive hand gestures."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

HAND_GESTURES = [
    Gesture("hands_open", 0.5, 0.5, 0.0, "neutral"),
    Gesture("palms_up", 0.5, 0.5, 0.1, "tilt"),
    Gesture("hands_clasped", 0.3, 0.3, 0.0, "neutral"),
    Gesture("count_one", 0.4, 0.2, 0.0, "tilt"),
    Gesture("count_two", 0.6, 0.3, 0.0, "tilt"),
    Gesture("count_three", 0.8, 0.4, 0.1, "tilt"),
]


def gestures() -> list[Gesture]:
    return HAND_GESTURES
