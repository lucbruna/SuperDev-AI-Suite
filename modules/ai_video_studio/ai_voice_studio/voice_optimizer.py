"""Voice Optimizer — smart parameter defaults and synthesis tuning."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_voice_studio.synthesis.emotion_controller import emotion_prosody


class VoiceOptimizer:
    """Adjusts synthesis parameters to balance speed and expressiveness."""

    def __init__(self) -> None:
        # Per-content-length targets: short clips can afford richer prosody.
        self._tuning: dict[str, dict[str, Any]] = {
            "short": {"max_chars": 120, "use_streaming": False},
            "medium": {"max_chars": 500, "use_streaming": False},
            "long": {"max_chars": 2000, "use_streaming": True},
        }

    def bucket(self, text: str) -> str:
        n = len(text)
        for kind, cfg in self._tuning.items():
            if n <= cfg["max_chars"]:
                return kind
        return "long"

    def tune(self, text: str, params: dict[str, Any]) -> dict[str, Any]:
        """Return synthesis params with sensible defaults applied."""
        bucket = self.bucket(text)
        tuned = dict(params)
        tuned.setdefault("voice_id", "default")
        tuned.setdefault("language", "en")
        tuned.setdefault("speed", 1.0)
        tuned.setdefault("pitch", 1.0)
        tuned.setdefault("emotion", "neutral")
        if tuned.get("emotion") and tuned["emotion"] != "neutral":
            p = emotion_prosody(str(tuned["emotion"]))
            tuned["speed"] *= p["rate"]
            tuned["pitch"] *= p["pitch"]
        tuned["_bucket"] = bucket
        tuned["_streaming"] = self._tuning[bucket]["use_streaming"]
        return tuned
