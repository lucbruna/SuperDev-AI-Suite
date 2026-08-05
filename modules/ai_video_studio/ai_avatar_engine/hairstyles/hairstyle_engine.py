"""Hairstyle engine — selects hairstyles from all catalogs."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.hairstyles.color_engine import (
    get_color_engine,
)

_CATALOGS = {
    "short": "short_styles",
    "medium": "medium_styles",
    "long": "long_styles",
    "curly": "curly_styles",
    "straight": "straight_styles",
    "afro": "afro_styles",
    "beard": "beard_styles",
    "mustache": "mustache_styles",
    "eyebrows": "eyebrow_styles",
}


class HairstyleEngine:
    """Aggregates hairstyle catalogs and applies colors."""

    def styles(self, catalog: str | None = None) -> list[dict[str, Any]]:
        if catalog is not None:
            return self._load(catalog)
        all_styles: list[dict[str, Any]] = []
        for name in _CATALOGS:
            all_styles.extend(self._load(name))
        return all_styles

    def catalogs(self) -> list[str]:
        return list(_CATALOGS)

    def select(self, catalog: str, style_id: str | None = None,
               color: str = "brown") -> dict[str, Any]:
        styles = self._load(catalog)
        style = next((s for s in styles if s["id"] == style_id), styles[0])
        return {**style, "color": get_color_engine().resolve(color)}

    def _load(self, catalog: str) -> list[dict[str, Any]]:
        module_name = _CATALOGS.get(catalog)
        if module_name is None:
            raise KeyError(f"unknown hairstyle catalog '{catalog}'")
        module = __import__(f"{__name__.rsplit('.', 1)[0]}.{module_name}",
                            fromlist=["styles"])
        return list(module.styles())


_hairstyle_engine: HairstyleEngine | None = None


def get_hairstyle_engine() -> HairstyleEngine:
    """Return the shared hairstyle engine singleton."""
    global _hairstyle_engine
    if _hairstyle_engine is None:
        _hairstyle_engine = HairstyleEngine()
    return _hairstyle_engine
