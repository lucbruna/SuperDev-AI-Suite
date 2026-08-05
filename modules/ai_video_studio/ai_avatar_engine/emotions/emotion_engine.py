"""Emotion engine — resolves named emotions and produces timelines."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.emotions.emotional_blending import (
    get_emotional_blending,
)
from modules.ai_video_studio.ai_avatar_engine.emotions.neutral import EmotionPreset

EMOTION_MODULES = (
    "neutral", "happy", "sad", "angry", "fear", "surprise", "disgust",
    "excitement", "confidence", "empathy", "curiosity", "humor",
)

_EMOTION_CACHE: dict[str, EmotionPreset] = {}


class EmotionEngine:
    """Registry + resolution for emotion presets."""

    def names(self) -> list[str]:
        return list(EMOTION_MODULES)

    def get(self, name: str) -> EmotionPreset:
        if name not in _EMOTION_CACHE:
            if name not in EMOTION_MODULES:
                raise KeyError(f"unknown emotion '{name}'")
            module = __import__(f"{__name__.rsplit('.', 1)[0]}.{name}", fromlist=["preset"])
            _EMOTION_CACHE[name] = module.preset()
        return _EMOTION_CACHE[name]

    def to_dict(self, name: str) -> dict[str, Any]:
        return self.get(name).to_dict()

    def timeline(self, segments: list[dict[str, Any]], *, duration: float,
                 fps: int = 24) -> list[dict[str, Any]]:
        """Per-frame emotion timeline with easing between states."""
        return get_emotional_blending().timeline(segments, duration=duration, fps=fps)


_emotion_engine: EmotionEngine | None = None


def get_emotion_engine() -> EmotionEngine:
    """Return the shared emotion engine singleton."""
    global _emotion_engine
    if _emotion_engine is None:
        _emotion_engine = EmotionEngine()
    return _emotion_engine
