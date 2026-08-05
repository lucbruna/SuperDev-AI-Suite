"""Emotion Controller — maps emotions to prosody (rate/pitch/energy/vibrato)."""
from __future__ import annotations


EMOTIONS: dict[str, dict[str, float]] = {
    "neutral": {"rate": 1.00, "pitch": 1.00, "energy": 0.50, "vibrato": 0.00},
    "happy": {"rate": 1.12, "pitch": 1.08, "energy": 0.72, "vibrato": 0.02},
    "excited": {"rate": 1.22, "pitch": 1.15, "energy": 0.85, "vibrato": 0.03},
    "sad": {"rate": 0.90, "pitch": 0.92, "energy": 0.35, "vibrato": 0.01},
    "calm": {"rate": 0.95, "pitch": 1.00, "energy": 0.40, "vibrato": 0.00},
    "angry": {"rate": 1.18, "pitch": 1.04, "energy": 0.92, "vibrato": 0.04},
    "fearful": {"rate": 1.20, "pitch": 1.12, "energy": 0.60, "vibrato": 0.05},
    "surprised": {"rate": 1.15, "pitch": 1.22, "energy": 0.80, "vibrato": 0.03},
    "serious": {"rate": 0.97, "pitch": 0.98, "energy": 0.55, "vibrato": 0.00},
    "whisper": {"rate": 0.88, "pitch": 1.10, "energy": 0.20, "vibrato": 0.00},
    "romantic": {"rate": 0.92, "pitch": 1.05, "energy": 0.45, "vibrato": 0.02},
    "melancholic": {"rate": 0.87, "pitch": 0.90, "energy": 0.30, "vibrato": 0.01},
}

_ALIASES = {
    "joyful": "happy",
    "cheerful": "happy",
    "sorrowful": "sad",
    "upset": "angry",
    "terrified": "fearful",
    "amazed": "surprised",
    "neutral": "neutral",
    "energetic": "excited",
}


def emotion_prosody(emotion: str | None) -> dict[str, float]:
    """Return ``{rate, pitch, energy, vibrato}`` for an emotion name."""
    key = _ALIASES.get((emotion or "neutral").lower(), (emotion or "neutral").lower())
    return dict(EMOTIONS.get(key, EMOTIONS["neutral"]))


def supported_emotions() -> list[str]:
    return sorted(set(EMOTIONS) | set(_ALIASES))
