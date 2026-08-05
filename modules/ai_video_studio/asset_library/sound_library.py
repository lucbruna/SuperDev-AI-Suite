"""Sound library — sound effect assets."""
from __future__ import annotations

from typing import Any


class SoundLibrary:
    """Catalogues sound effects by category."""

    def __init__(self) -> None:
        self._sounds: dict[str, dict[str, Any]] = {}

    def register(self, name: str, *, ref: str, category: str = "ambient", duration_seconds: float = 2.0) -> None:
        self._sounds[name] = {
            "name": name,
            "ref": ref,
            "category": category,
            "duration_seconds": duration_seconds,
        }

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._sounds[name]) if name in self._sounds else None

    def by_category(self, category: str) -> list[str]:
        return [name for name, s in self._sounds.items() if s["category"] == category]

    def names(self) -> list[str]:
        return list(self._sounds.keys())
