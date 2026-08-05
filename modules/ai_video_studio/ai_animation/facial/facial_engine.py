"""Facial engine — orchestrate facial expression animation."""
from __future__ import annotations

from typing import Any


class FacialEngine:
    """Plans a facial animation from requested expression/emotion."""

    def plan(self, config: dict[str, Any]) -> dict[str, Any]:
        emotion = config.get("emotion", "neutral")
        return {
            "emotion": emotion,
            "blink": config.get("blink", True),
            "speech": config.get("speech", ""),
            "lip_sync": bool(config.get("speech")),
            "smile_amount": config.get("smile_amount", 0.0),
        }

    def set_emotion(self, plan: dict[str, Any], emotion: str) -> None:
        plan["emotion"] = emotion
