"""Effects library — VFX and post-processing effect presets."""
from __future__ import annotations

from typing import Any


class EffectsLibrary:
    """Catalogues visual effects and post-process presets."""

    def __init__(self) -> None:
        self._effects: dict[str, dict[str, Any]] = {}

    def register(self, name: str, *, ref: str, category: str = "particle", intensity_default: float = 0.5) -> None:
        self._effects[name] = {
            "name": name,
            "ref": ref,
            "category": category,
            "intensity_default": intensity_default,
        }

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._effects[name]) if name in self._effects else None

    def by_category(self, category: str) -> list[str]:
        return [name for name, e in self._effects.items() if e["category"] == category]

    def names(self) -> list[str]:
        return list(self._effects.keys())
