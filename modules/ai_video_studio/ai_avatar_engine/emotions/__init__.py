"""Emotions — emotional expression presets and blending.

Each emotion module defines an :class:`EmotionPreset` (facial + body +
voice parameters). The ``EmotionEngine`` resolves named emotions and blends
between them over time.
"""
from modules.ai_video_studio.ai_avatar_engine.emotions.emotion_engine import (
    EmotionEngine,
    get_emotion_engine,
)

__all__ = ["EmotionEngine", "get_emotion_engine"]
