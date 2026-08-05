"""Teaching gestures — instructional gesture vocabulary."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

TEACHING_GESTURES = [
    Gesture("teach_explain", 0.6, 0.6, 0.1, "neutral"),
    Gesture("teach_point_board", 0.9, 0.3, 0.2, "tilt"),
    Gesture("teach_enumerate", 0.5, 0.5, 0.0, "nod"),
    Gesture("teach_compare", 0.7, 0.3, 0.0, "neutral"),
    Gesture("teach_write", 0.4, 0.8, 0.1, "down"),
]


def gestures() -> list[Gesture]:
    return TEACHING_GESTURES
