"""Emotion mapper — map emotions to facial parameter sets."""
from __future__ import annotations

from typing import Any

_EMOTIONS: dict[str, dict[str, Any]] = {
    "happy": {"brow_raise": 0.4, "smile": 0.8, "eye_open": 0.2},
    "sad": {"brow_raise": -0.3, "smile": -0.4, "eye_open": -0.3},
    "angry": {"brow_raise": -0.5, "smile": -0.6, "eye_open": 0.4},
    "surprised": {"brow_raise": 0.9, "smile": 0.0, "eye_open": 0.9},
    "fear": {"brow_raise": 0.6, "smile": -0.5, "eye_open": 0.7},
    "disgust": {"brow_raise": -0.2, "smile": -0.7, "eye_open": -0.2},
    "neutral": {"brow_raise": 0.0, "smile": 0.0, "eye_open": 0.0},
}


class EmotionMapper:
    """Converts an emotion label into facial animation parameters."""

    def map(self, emotion: str) -> dict[str, Any]:
        if emotion not in _EMOTIONS:
            raise ValueError(f"Unknown emotion '{emotion}'")
        return dict(_EMOTIONS[emotion])

    def available_emotions(self) -> list[str]:
        return list(_EMOTIONS.keys())
