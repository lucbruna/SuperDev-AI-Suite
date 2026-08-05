"""Automatic Ads — short ad briefs generated from product inputs."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class AutomaticAdsGenerator:
    """Builds short ad scripts (15–30s) from product attributes."""

    def generate(self, *, product: str = "smart coffee machine", hook: str = "Perfect coffee every morning",
                 cta: str = "Order now", voice: str = "default") -> dict[str, Any]:
        title = f"Ad — {product}"
        scenes = [
            hook,
            f"Meet {product} — designed for you.",
            "Simple, reliable and built to impress.",
            cta + " — visit our store today.",
        ]
        return build_brief("crm", title, scenes, style="vibrant", voice=voice,
                           product=product, hook=hook, cta=cta,
                           seconds_per_scene=3.0).to_dict()


_automatic_ads_generator: AutomaticAdsGenerator | None = None


def get_automatic_ads_generator() -> AutomaticAdsGenerator:
    global _automatic_ads_generator
    if _automatic_ads_generator is None:
        _automatic_ads_generator = AutomaticAdsGenerator()
    return _automatic_ads_generator
