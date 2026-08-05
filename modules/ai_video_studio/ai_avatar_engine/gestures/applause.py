"""Applause — celebratory clapping gestures."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

APPLAUSE_GESTURES = [
    Gesture("applause_clap", 0.9, 0.9, 0.1, "neutral"),
    Gesture("applause_cheer", 0.95, 0.95, 0.3, "up"),
    Gesture("applause_standing_ovation", 1.0, 1.0, 0.4, "up"),
]


def gestures() -> list[Gesture]:
    return APPLAUSE_GESTURES
