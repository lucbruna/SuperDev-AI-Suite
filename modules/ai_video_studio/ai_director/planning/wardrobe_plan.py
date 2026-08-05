"""Wardrobe plan — plans costume needs for the production."""
from __future__ import annotations

from typing import Any


class WardrobePlan:
    """Defines wardrobe requirements per character."""

    def build(self, characters: list[str] | None = None) -> dict[str, Any]:
        names = characters or ["Host", "Guest"]
        return {name: {"outfits": 2, "style": "business casual"} for name in names}


_wardrobe_plan: WardrobePlan | None = None


def get_wardrobe_plan() -> WardrobePlan:
    global _wardrobe_plan
    if _wardrobe_plan is None:
        _wardrobe_plan = WardrobePlan()
    return _wardrobe_plan
