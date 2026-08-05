"""Podcast skill — episode outline with timed segments, intro and outro."""
from __future__ import annotations
from typing import Any

_PROGRESSION = [
    "Cold open",
    "What is {topic}",
    "Why it matters",
    "Common pitfalls with {topic}",
    "Actionable steps",
    "Wrap-up and next episode",
]


class PodcastSkill:
    """Structure a podcast episode: segments, intro, outro and pacing."""

    skill_id = "podcast"
    skill_name = "Podcast"
    skill_version = "1.0.0"
    skill_description = "Podcast episode outline with timed segments and hooks."
    skill_category = "voice"
    skill_tags = ["voice", "podcast", "episode", "outline"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        topic: str,
        *,
        duration_minutes: float = 20.0,
        language: str = "en",
        segments: int = 3,
    ) -> dict[str, Any]:
        """Return a timed episode outline derived deterministically from the topic."""
        per = round(duration_minutes / max(1, segments), 1)
        segs = [
            {"title": _PROGRESSION[i % len(_PROGRESSION)].format(topic=topic), "minutes": per}
            for i in range(segments)
        ]
        return {
            "platform": "podcast",
            "topic": topic,
            "language": language,
            "intro": f"Welcome — today we unpack {topic}.",
            "outro": f"That wraps our look at {topic}. Thanks for listening.",
            "segments": segs,
            "duration_minutes": duration_minutes,
            "suggested_voice": "default",
        }
