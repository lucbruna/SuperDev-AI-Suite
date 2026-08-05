"""Vehicle library — vehicle asset catalog with specs."""
from __future__ import annotations

from typing import Any


class VehicleLibrary:
    """Catalogues vehicles with physics-relevant specs."""

    def __init__(self) -> None:
        self._vehicles: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        *,
        ref: str,
        vehicle_type: str = "car",
        mass_kg: float = 1200.0,
        max_speed_mps: float = 50.0,
    ) -> None:
        self._vehicles[name] = {
            "name": name,
            "ref": ref,
            "type": vehicle_type,
            "mass_kg": mass_kg,
            "max_speed_mps": max_speed_mps,
        }

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._vehicles[name]) if name in self._vehicles else None

    def names(self) -> list[str]:
        return list(self._vehicles.keys())
