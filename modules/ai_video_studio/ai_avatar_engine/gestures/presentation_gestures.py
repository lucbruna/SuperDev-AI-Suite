"""Presentation gestures — gestures for talks and slides."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

PRESENTATION_GESTURES = [
    Gesture("present_pointer", 0.8, 0.3, 0.1, "tilt"),
    Gesture("present_slide_change", 0.7, 0.7, 0.0, "neutral"),
    Gesture("present_emphasis", 0.9, 0.4, 0.2, "neutral"),
    Gesture("present_pause", 0.3, 0.3, 0.0, "neutral"),
    Gesture("present_welcome", 0.6, 0.6, 0.1, "neutral"),
]


def gestures() -> list[Gesture]:
    return PRESENTATION_GESTURES
