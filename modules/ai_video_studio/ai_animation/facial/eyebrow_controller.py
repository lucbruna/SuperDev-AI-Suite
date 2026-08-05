"""Eyebrow controller — eyebrow position by emotion."""
from __future__ import annotations

from typing import Any

_EMOTION_MAP = {
    "happy": {"raise": 0.4, "furrow": 0.0},
    "angry": {"raise": -0.2, "furrow": 0.7},
    "sad": {"raise": 0.1, "furrow": 0.3},
    "surprised": {"raise": 0.9, "furrow": 0.0},
    "neutral": {"raise": 0.0, "furrow": 0.0},
}


class EyebrowController:
    """Maps emotions to eyebrow transform values."""

    def pose(self, emotion: str = "neutral") -> dict[str, Any]:
        return dict(_EMOTION_MAP.get(emotion, _EMOTION_MAP["neutral"]))

    def available_emotions(self) -> list[str]:
        return list(_EMOTION_MAP.keys())
