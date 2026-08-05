"""Storyteller skill — narrative arc with narration-ready beats."""
from __future__ import annotations
from typing import Any


class StorytellerSkill:
    """Shape a story into beats ready for narration."""

    skill_id = "storyteller"
    skill_name = "Storyteller"
    skill_version = "1.0.0"
    skill_description = "Story arc (setup → tension → climax → resolution) for narration."
    skill_category = "voice"
    skill_tags = ["voice", "storytelling", "narrative", "beats"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        story: str,
        *,
        style: str = "fable",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return narration beats covering the full story arc."""
        beats = [
            {"beat": "Setup", "narration": f"Once, {story} began quietly."},
            {"beat": "Tension", "narration": f"But soon, {story} faced its first test."},
            {"beat": "Climax", "narration": f"And then came the moment {story} would be remembered for."},
            {"beat": "Resolution", "narration": f"In the end, {story} left a lesson worth telling."},
        ]
        return {
            "platform": "storyteller",
            "story": story,
            "style": style,
            "language": language,
            "beats": beats,
            "narration_style": "per_beat",
            "suggested_voice": "default",
        }
