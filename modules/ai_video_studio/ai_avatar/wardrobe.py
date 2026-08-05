"""Wardrobe — clothing and accessories for virtual presenters.

Each occasion maps to a coordinated outfit (jacket/top colors) plus a set
of optional accessories (glasses, watch, scarf, cap...). The engine uses
the wardrobe to dress an actor consistently across scenes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from modules.ai_video_studio.core.constants import AvatarStyle


@dataclass(frozen=True)
class Outfit:
    """A coordinated clothing set for a presenter."""

    name: str
    top_color: str
    accent_color: str
    accessories: list[str] = field(default_factory=list)
    style_hint: str = "neutral"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "top_color": self.top_color,
            "accent_color": self.accent_color,
            "accessories": list(self.accessories),
            "style_hint": self.style_hint,
        }


# ── The wardrobe catalog ─────────────────────────────────────────
WARDROBE: dict[str, Outfit] = {
    "business": Outfit("Business", "#2c3e50", "#e8c060", ["watch"]),
    "formal": Outfit("Formal", "#1a1a2e", "#c9a86a", ["watch", "tie"]),
    "casual": Outfit("Casual", "#5b8db8", "#f0e6d2", ["scarf"]),
    "tech": Outfit("Tech", "#1f2833", "#45a29e", ["glasses", "watch"]),
    "sport": Outfit("Sport", "#d9534f", "#f5f5f5", ["cap", "wristband"]),
    "minimal": Outfit("Minimal", "#404040", "#d0d0d0", []),
    "creative": Outfit("Creative", "#7b4b94", "#f2c14e", ["glasses"]),
    "formal_night": Outfit("Formal Night", "#0d0d0d", "#e8c060", ["watch", "tie"]),
}

_ACCESSORIES = ("glasses", "watch", "tie", "scarf", "cap", "wristband", "earrings", "necklace")


class Wardrobe:
    """Select outfits and accessories for any actor + occasion."""

    def __init__(self, catalog: dict[str, Outfit] | None = None) -> None:
        self._catalog = dict(catalog if catalog is not None else WARDROBE)

    def occasions(self) -> list[str]:
        return list(self._catalog)

    def get(self, occasion: str) -> Outfit:
        if occasion not in self._catalog:
            raise KeyError(f"unknown occasion '{occasion}'")
        return self._catalog[occasion]

    def select(
        self,
        occasion: str,
        *,
        style: str | None = None,
        actor_skin_tone: str | None = None,
    ) -> dict[str, Any]:
        """Pick an outfit; ``style`` nudges palette choices for stylized 2D actors."""
        outfit = self.get(occasion)
        result = outfit.to_dict()

        # Anime/cartoon/pixel actors get more saturated, playful palettes.
        if style in (AvatarStyle.ANIME.value, AvatarStyle.CARTOON.value):
            result["top_color"] = "#e07be0" if style == AvatarStyle.ANIME.value else "#f2a33c"
            result["accent_color"] = "#ffffff"
            result["style_hint"] = "playful"
        elif style == AvatarStyle.PIXEL_ART.value:
            result["top_color"] = "#4a4ae0"
            result["accent_color"] = "#e0e04a"
            result["style_hint"] = "retro"
        elif style == AvatarStyle.MINIMALIST.value:
            result["top_color"] = "#5a5a5a"
            result["accent_color"] = "#e0e0e0"
            result["style_hint"] = "clean"
        return result

    def accessories_for(self, occasion: str, *, count: int = 1) -> list[str]:
        """Return up to ``count`` accessories that fit the occasion."""
        outfit = self.get(occasion)
        available = list(outfit.accessories) or [a for a in _ACCESSORIES if a != "tie"]
        return available[:count]


_wardrobe: Wardrobe | None = None


def get_wardrobe() -> Wardrobe:
    """Return the shared wardrobe singleton."""
    global _wardrobe
    if _wardrobe is None:
        _wardrobe = Wardrobe()
    return _wardrobe
