"""Waving — greeting/goodbye waving gestures."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

WAVING_GESTURES = [
    Gesture("wave_greet", 0.85, 0.2, 0.0, "neutral"),
    Gesture("wave_goodbye", 0.85, 0.2, 0.0, "neutral"),
    Gesture("wave_hello_overhead", 0.95, 0.3, 0.1, "up"),
]


def gestures() -> list[Gesture]:
    return WAVING_GESTURES
