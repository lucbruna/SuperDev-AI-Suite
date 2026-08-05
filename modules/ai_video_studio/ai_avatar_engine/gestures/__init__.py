"""Gestures — automatic gesture libraries by context.

Every gesture module exposes a list of :class:`Gesture` objects (arm/lean/
head parameters). The ``GestureEngine`` aggregates them and plans gesture
timelines for scripts and scenes.
"""
from modules.ai_video_studio.ai_avatar_engine.gestures.gesture_engine import (
    GestureEngine,
    get_gesture_engine,
)

__all__ = ["GestureEngine", "get_gesture_engine"]
