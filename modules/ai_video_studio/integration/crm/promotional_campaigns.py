"""Promotional Campaigns — seasonal and event-driven promo briefs."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief

_SEASONS: dict[str, str] = {
    "black_friday": "Black Friday deals are live",
    "christmas": "Holiday gift guide",
    "new_year": "New year, new offers",
    "summer": "Summer sale is on",
    "anniversary": "Celebrating our anniversary",
}


class PromotionalCampaignsGenerator:
    """Builds seasonal promotion narration scripts."""

    def generate(self, *, season: str = "black_friday", offer: str = "up to 50% off",
                 voice: str = "default") -> dict[str, Any]:
        season = season if season in _SEASONS else "black_friday"
        title = _SEASONS[season]
        scenes = [
            f"{title} — {offer}.",
            "Hand-picked favorites at unbeatable prices.",
            "Stock is limited and prices reset soon.",
            "Shop now and share the offer with friends.",
        ]
        return build_brief("crm", title, scenes, style="vibrant", voice=voice,
                           season=season, offer=offer).to_dict()


_promotional_campaigns_generator: PromotionalCampaignsGenerator | None = None


def get_promotional_campaigns_generator() -> PromotionalCampaignsGenerator:
    global _promotional_campaigns_generator
    if _promotional_campaigns_generator is None:
        _promotional_campaigns_generator = PromotionalCampaignsGenerator()
    return _promotional_campaigns_generator
