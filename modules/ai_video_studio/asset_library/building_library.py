"""Building library — architectural and structural assets."""
from __future__ import annotations

from typing import Any


class BuildingLibrary:
    """Catalogues buildings by architectural style and function."""

    def __init__(self) -> None:
        self._buildings: dict[str, dict[str, Any]] = {}

    def register(self, name: str, *, ref: str, style: str = "modern", floors: int = 3) -> None:
        self._buildings[name] = {"name": name, "ref": ref, "style": style, "floors": floors}

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._buildings[name]) if name in self._buildings else None

    def by_style(self, style: str) -> list[str]:
        return [name for name, b in self._buildings.items() if b["style"] == style]

    def names(self) -> list[str]:
        return list(self._buildings.keys())
