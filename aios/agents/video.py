"""VideoAgent: deterministic storyboarding and shot planning from a script."""
from __future__ import annotations

import re
from typing import Any

from aios.agents.base_agent import BaseAgent


class VideoAgent(BaseAgent):
    def __init__(self, name: str = "video", **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="video",
            capabilities=["storyboarding", "shot_planning", "video_editing"],
            description="Plans shots and storyboards from scripts",
            **kwargs,
        )

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        script = input_data if isinstance(input_data, str) else str(input_data.get("script", ""))
        sentences = [s.strip() for s in re.split(r"[.!?\n]+", script) if s.strip()]
        if not sentences:
            sentences = [script or "empty script"]
        shots = [
            {
                "shot": i,
                "description": sentence[:60],
                "duration_sec": min(10, max(2, len(sentence) // 12)),
                "type": "closeup" if i % 2 == 1 else "wide",
            }
            for i, sentence in enumerate(sentences, start=1)
        ]
        return {
            "script": script,
            "shots": shots,
            "total_shots": len(shots),
            "total_duration_sec": sum(shot["duration_sec"] for shot in shots),
            "format": context.get("format", "16:9"),
        }
