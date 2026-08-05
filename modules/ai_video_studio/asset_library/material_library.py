"""Material library — material definitions for rendering."""
from __future__ import annotations

from typing import Any


class MaterialLibrary:
    """Stores material presets (PBR parameters)."""

    def __init__(self) -> None:
        self._materials: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        *,
        base_color: tuple[float, float, float] = (1, 1, 1),
        roughness: float = 0.5,
        metallic: float = 0.0,
    ) -> None:
        if not 0 <= roughness <= 1 or not 0 <= metallic <= 1:
            raise ValueError("roughness and metallic must be in [0, 1]")
        self._materials[name] = {
            "name": name,
            "base_color": list(base_color),
            "roughness": roughness,
            "metallic": metallic,
        }

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._materials[name]) if name in self._materials else None

    def names(self) -> list[str]:
        return list(self._materials.keys())
