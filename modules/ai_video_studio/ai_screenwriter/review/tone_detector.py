"""Tone detector — identifies the emotional tone of a script."""
from __future__ import annotations

from typing import Any


class ToneDetector:
    """Detects tone from script text."""

    def detect(self, text: str) -> dict[str, Any]:
        lowered = text.lower()
        if any(word in lowered for word in ("urgente", "agora", "rápido", "já")):
            tone = "urgent"
        elif any(word in lowered for word in ("diversão", "engraçado", "risada", "piada")):
            tone = "playful"
        elif any(word in lowered for word in ("emocionante", "história", "jornada")):
            tone = "emotional"
        else:
            tone = "informative"
        return {"tone": tone, "confidence": 0.7}


_tone_detector: ToneDetector | None = None


def get_tone_detector() -> ToneDetector:
    global _tone_detector
    if _tone_detector is None:
        _tone_detector = ToneDetector()
    return _tone_detector
