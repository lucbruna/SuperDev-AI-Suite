"""Documentary skill — observational documentary outline from a topic."""
from __future__ import annotations
from typing import Any


class DocumentarySkill:
    """Plan a documentary narrative arc (hook → context → climax)."""

    skill_id = "documentary"
    skill_name = "Documentary"
    skill_version = "1.0.0"
    skill_description = "Observational documentary outline with a five-beat narrative arc."
    skill_category = "video"
    skill_tags = ["video", "documentary", "narrative", "16:9"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        topic: str,
        *,
        duration: float = 8.0,
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a documentary outline derived deterministically from the topic."""
        outline = [
            {"segment": "Hook", "content": f"Open with the most striking image of {topic}."},
            {"segment": "Context", "content": f"Establish where and why {topic} matters."},
            {"segment": "Interviews", "content": f"Let the people behind {topic} speak first."},
            {"segment": "Build-up", "content": f"Follow the turning points shaping {topic}."},
            {"segment": "Climax", "content": f"Reach the moment that defines {topic}."},
        ]
        return {
            "platform": "documentary",
            "topic": topic,
            "aspect_ratio": "16:9",
            "outline": outline,
            "estimated_duration_s": duration * 60.0,
            "language": language,
            "tone": "observational",
        }
