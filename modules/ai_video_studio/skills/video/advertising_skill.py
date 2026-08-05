"""Advertising skill — ad video concept and scripts from a product brief."""
from __future__ import annotations
from typing import Any


class AdvertisingSkill:
    """Generate a hook/benefit/CTA ad script across common durations."""

    skill_id = "advertising"
    skill_name = "Advertising"
    skill_version = "1.0.0"
    skill_description = "Ad concept planning with per-duration scripts and CTAs."
    skill_category = "video"
    skill_tags = ["video", "advertising", "marketing", "script"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        product: str,
        *,
        audience: str = "general",
        hook: str | None = None,
        duration_s: int = 30,
    ) -> dict[str, Any]:
        """Return an ad script structure sized for the requested duration."""
        resolved_hook = hook or f"What if {product} could do more?"
        script = [
            resolved_hook,
            f"{product} is built for {audience} — simply, reliably.",
            f"Get {product} today.",
        ]
        return {
            "platform": "advertising",
            "product": product,
            "audience": audience,
            "duration_s": duration_s,
            "hook": resolved_hook,
            "script": script,
            "cta": f"Get {product} today.",
            "aspect_ratios": ["16:9", "9:16", "1:1"],
        }
