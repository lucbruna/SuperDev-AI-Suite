"""Emotion Alignment — maps line emotions to TTS prosody."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_voice_studio.synthesis.emotion_controller import emotion_prosody

# Rule-based emotion hints from punctuation and keywords.
_EXCLAMATIONS = "!?"
_KEYWORDS = {
    "happy": ("happy", "joy", "great", "wonderful", "amazing", "love"),
    "sad": ("sad", "sorry", "miss", "cry", "alone", "lost"),
    "angry": ("angry", "mad", "furious", "hate", "never", "stop"),
    "surprised": ("wow", "what", "really", "no way", "unbelievable"),
    "calm": ("calm", "peace", "quiet", "slowly", "gently"),
}


def infer_emotion(text: str) -> str:
    """Best-effort emotion guess for a line."""
    lowered = text.lower()
    if any(ch in lowered for ch in _EXCLAMATIONS):
        return "excited"
    for emotion, words in _KEYWORDS.items():
        if any(w in lowered for w in words):
            return emotion
    return "neutral"


def emotion_prosody_for_line(text: str, *, explicit: str | None = None) -> dict[str, float]:
    """Return ``{emotion, rate, pitch, energy}`` for a line."""
    emotion = explicit or infer_emotion(text)
    p = emotion_prosody(emotion)
    return {"emotion": emotion, **p}


def apply_to_lines(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach per-line emotion prosody to a layout."""
    out: list[dict[str, Any]] = []
    for line in lines:
        entry = dict(line)
        entry["emotion"] = emotion_prosody_for_line(entry.get("text", ""))
        out.append(entry)
    return out
