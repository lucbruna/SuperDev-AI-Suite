"""Brand strategy skill — positioning and messaging framework."""
from __future__ import annotations
from typing import Any


class BrandStrategySkill:
    """Define brand positioning, personality, and messaging pillars."""

    skill_id = "brand_strategy"
    skill_name = "Brand Strategy"
    skill_version = "1.0.0"
    skill_description = "Brand positioning, personality, and three messaging pillars."
    skill_category = "marketing"
    skill_tags = ["marketing", "brand", "positioning", "strategy"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        brand: str,
        *,
        category: str = "product",
        audience: str = "the target market",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a positioning statement and messaging pillars."""
        pillars = ("Clarity", "Trust", "Outcome")
        return {
            "brand": brand,
            "category": category,
            "audience": audience,
            "language": language,
            "positioning": (
                f"For {audience}, {brand} is the {category} "
                f"that delivers the outcome others promise."
            ),
            "personality": ["helpful", "direct", "optimistic"],
            "pillars": [
                {"name": name, "message": f"{brand} makes {category} simpler for {audience}."}
                for name in pillars
            ],
            "voice": "conversational and confident",
        }
