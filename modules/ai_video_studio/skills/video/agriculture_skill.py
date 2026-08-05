"""Agriculture skill — farm-story video plan with captions and platforms."""
from __future__ import annotations
from typing import Any


class AgricultureSkill:
    """Plan a field-to-table farm story with localized captions."""

    skill_id = "agriculture"
    skill_name = "Agriculture"
    skill_version = "1.0.0"
    skill_description = "Farm-story video arc with captions for ag audiences."
    skill_category = "video"
    skill_tags = ["video", "agriculture", "storytelling", "captions"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        story: str,
        *,
        language: str = "pt",
        duration: float = 6.0,
    ) -> dict[str, Any]:
        """Return a four-beat farm-story arc with caption lines."""
        captions = [
            f"From the field: {story}",
            "Grown with care, step by step.",
            f"The story behind {story}.",
            "From farm to your table.",
        ]
        return {
            "platform": "agriculture",
            "story": story,
            "arc": {
                "hook": f"Start in the middle of the field: {story}.",
                "field": "Show the daily work and the land.",
                "table": "Bring the harvest to the table.",
                "close": f"End with why {story} matters to the community.",
            },
            "captions_language": language,
            "captions": captions,
            "target_platforms": ["YouTube", "Instagram Reels", "TikTok"],
            "estimated_duration_s": duration * 60.0,
        }
