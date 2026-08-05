"""Fabric materials — fabric property catalog for garments."""
from __future__ import annotations

from typing import Any

FABRICS: dict[str, dict[str, Any]] = {
    "cotton": {"drape": 0.4, "sheen": 0.1, "stretch": 0.3, "weight": "medium"},
    "wool": {"drape": 0.6, "sheen": 0.2, "stretch": 0.2, "weight": "heavy"},
    "silk": {"drape": 0.9, "sheen": 0.9, "stretch": 0.1, "weight": "light"},
    "linen": {"drape": 0.5, "sheen": 0.15, "stretch": 0.1, "weight": "light"},
    "denim": {"drape": 0.3, "sheen": 0.1, "stretch": 0.4, "weight": "heavy"},
    "leather": {"drape": 0.1, "sheen": 0.7, "stretch": 0.0, "weight": "heavy"},
    "polyester": {"drape": 0.6, "sheen": 0.6, "stretch": 0.5, "weight": "medium"},
    "velvet": {"drape": 0.8, "sheen": 0.8, "stretch": 0.2, "weight": "heavy"},
}


class FabricMaterials:
    """Provides fabric properties for garment generation."""

    def get(self, fabric: str) -> dict[str, Any]:
        if fabric not in FABRICS:
            raise KeyError(f"unknown fabric '{fabric}'")
        return dict(FABRICS[fabric])

    def names(self) -> list[str]:
        return list(FABRICS)


_fabric_materials: FabricMaterials | None = None


def get_fabric_materials() -> FabricMaterials:
    global _fabric_materials
    if _fabric_materials is None:
        _fabric_materials = FabricMaterials()
    return _fabric_materials
