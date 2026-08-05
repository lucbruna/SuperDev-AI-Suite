"""Vegetation library — plant and foliage assets."""
from __future__ import annotations

from typing import Any


class VegetationLibrary:
    """Catalogues vegetation with growth/simulation metadata."""

    def __init__(self) -> None:
        self._plants: dict[str, dict[str, Any]] = {}

    def register(self, name: str, *, ref: str, biome: str = "temperate", animated: bool = True) -> None:
        self._plants[name] = {"name": name, "ref": ref, "biome": biome, "animated": animated}

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._plants[name]) if name in self._plants else None

    def by_biome(self, biome: str) -> list[str]:
        return [name for name, p in self._plants.items() if p["biome"] == biome]

    def names(self) -> list[str]:
        return list(self._plants.keys())
