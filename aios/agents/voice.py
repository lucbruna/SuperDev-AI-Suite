"""VoiceAgent: deterministic TTS segment planning and duration estimates."""
from __future__ import annotations

import re
from typing import Any

from aios.agents.base_agent import BaseAgent


class VoiceAgent(BaseAgent):
    def __init__(self, name: str = "voice", **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="voice",
            capabilities=["text_to_speech", "voiceover_planning", "pronunciation"],
            description="Plans voiceover segments and estimates durations",
            **kwargs,
        )

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        text = input_data if isinstance(input_data, str) else str(input_data.get("text", ""))
        if isinstance(input_data, dict):
            voice = input_data.get("voice") or context.get("voice", "neutral")
        else:
            voice = context.get("voice", "neutral")
        wpm = max(1, int(context.get("wpm", 150)))
        words = len([w for w in text.split() if w])
        segments = [
            {
                "segment": i,
                "text": sentence[:60],
                "est_sec": round(max(1.0, len(sentence.split()) / wpm * 60), 2),
            }
            for i, sentence in enumerate([s for s in re.split(r"[.!?\n]+", text) if s.strip()], start=1)
        ]
        return {
            "voice": voice,
            "chars": len(text),
            "words": words,
            "estimated_duration_sec": round(words / wpm * 60, 2),
            "segments": segments,
            "language": context.get("language", "pt-BR"),
        }
