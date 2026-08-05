"""Social planner skill — a content calendar for social channels."""
from __future__ import annotations
from typing import Any


class SocialPlannerSkill:
    """Build a weekly multi-channel social content calendar."""

    skill_id = "social_planner"
    skill_name = "Social Planner"
    skill_version = "1.0.0"
    skill_description = "Weekly multi-channel social content calendar for a brand."
    skill_category = "marketing"
    skill_tags = ["marketing", "social", "calendar", "content"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        brand: str,
        *,
        days: int = 5,
        channels: tuple[str, ...] = ("instagram", "tiktok", "linkedin"),
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a calendar of one post per day per channel."""
        formats = ("educational", "behind-the-scenes", "promotional", "community", "story")
        calendar: list[dict[str, Any]] = []
        for day in range(1, days + 1):
            for channel in channels:
                calendar.append(
                    {
                        "day": day,
                        "channel": channel,
                        "format": formats[(day + len(channel)) % len(formats)],
                        "content": f"{brand} {formats[(day + len(channel)) % len(formats)]} post for day {day}.",
                        "cta": "Learn more" if day % 3 else "Join the conversation",
                    }
                )
        return {
            "brand": brand,
            "days": days,
            "channels": list(channels),
            "language": language,
            "calendar": calendar,
            "cadence": f"{days} days x {len(channels)} channels",
        }
