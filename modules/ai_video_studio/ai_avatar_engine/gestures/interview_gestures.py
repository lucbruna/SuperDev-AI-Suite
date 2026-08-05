"""Interview gestures — gesture vocabulary for interviews/podcasts."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

INTERVIEW_GESTURES = [
    Gesture("interview_listen", 0.1, 0.1, 0.2, "tilt"),
    Gesture("interview_consider", 0.2, 0.2, 0.1, "tilt_left"),
    Gesture("interview_agree", 0.3, 0.3, 0.0, "nod"),
    Gesture("interview_clarify", 0.5, 0.5, 0.0, "tilt"),
    Gesture("interview_conclude", 0.4, 0.4, 0.0, "neutral"),
]


def gestures() -> list[Gesture]:
    return INTERVIEW_GESTURES
