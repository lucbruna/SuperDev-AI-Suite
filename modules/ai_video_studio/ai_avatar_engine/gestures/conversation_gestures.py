"""Conversation gestures — casual conversational vocabulary."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

CONVERSATION_GESTURES = [
    Gesture("chat_engage", 0.4, 0.4, 0.1, "tilt"),
    Gesture("chat_laugh", 0.5, 0.5, -0.1, "neutral"),
    Gesture("chat_question", 0.5, 0.5, 0.2, "tilt_left"),
    Gesture("chat_story", 0.6, 0.6, 0.0, "neutral"),
    Gesture("chat_react", 0.7, 0.3, 0.1, "nod"),
]


def gestures() -> list[Gesture]:
    return CONVERSATION_GESTURES
