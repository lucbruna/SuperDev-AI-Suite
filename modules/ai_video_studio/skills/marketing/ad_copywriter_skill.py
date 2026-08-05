"""Ad copywriter skill — persuasive ad copy for any product and channel."""
from __future__ import annotations
from typing import Any


class AdCopywriterSkill:
    """Write AIDA-structured ad copy adapted to the target channel."""

    skill_id = "ad_copywriter"
    skill_name = "Ad Copywriter"
    skill_version = "1.0.0"
    skill_description = "Persuasive ad copy (AIDA) for a product on a given channel."
    skill_category = "marketing"
    skill_tags = ["marketing", "advertising", "copywriting", "aida"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        product: str,
        audience: str,
        *,
        channel: str = "social",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return an ad copy broken into AIDA sections."""
        return {
            "product": product,
            "audience": audience,
            "channel": channel,
            "language": language,
            "framework": "AIDA",
            "headline": f"{product}: built for {audience}",
            "sections": [
                {"part": "Attention", "content": f"Stop scrolling — {product} changes how {audience} works."},
                {"part": "Interest", "content": f"Most {audience} lose time on tasks {product} automates."},
                {"part": "Desire", "content": f"Imagine your week with {product}: faster, calmer, sharper."},
                {"part": "Action", "content": f"Try {product} today and see the difference yourself."},
            ],
            "tone": "persuasive",
            "length_hint": "short" if channel == "social" else "medium",
        }
