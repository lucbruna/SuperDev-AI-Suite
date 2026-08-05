"""Training Generator — compliance and skills training videos."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief

_TOPICS: dict[str, str] = {
    "compliance": "company policies and compliance essentials",
    "safety": "workplace safety and emergency procedures",
    "leadership": "leadership fundamentals for new managers",
    "tooling": "how to use our internal tools",
}


class TrainingGenerator:
    """Builds training narration scripts for HR topics."""

    def generate(self, *, topic: str = "compliance", audience: str = "all employees",
                 voice: str = "default") -> dict[str, Any]:
        topic = topic if topic in _TOPICS else "compliance"
        title = f"Training — {topic.replace('_', ' ')}"
        scenes = [
            f"Training module for {audience}: {_TOPICS[topic]}.",
            "Key rules are summarized in three minutes.",
            "Watch the examples, then take the short quiz.",
            "Your completion is recorded automatically.",
        ]
        return build_brief("human_resources", title, scenes, voice=voice,
                           topic=topic, audience=audience).to_dict()


_training_generator: TrainingGenerator | None = None


def get_training_generator() -> TrainingGenerator:
    global _training_generator
    if _training_generator is None:
        _training_generator = TrainingGenerator()
    return _training_generator
