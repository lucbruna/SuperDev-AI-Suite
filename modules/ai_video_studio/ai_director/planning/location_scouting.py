"""Location scouting — suggests and evaluates shooting locations."""
from __future__ import annotations

from typing import Any


class LocationScouting:
    """Evaluates location candidates."""

    def evaluate(self, candidates: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        base = candidates or [
            {"name": "Studio", "cost": 500.0, "light_control": 1.0},
            {"name": "Office", "cost": 0.0, "light_control": 0.6},
            {"name": "Outdoors", "cost": 0.0, "light_control": 0.2},
        ]
        scored = []
        for candidate in base:
            score = candidate.get("light_control", 0.5) * 0.7 + (1.0 - min(1.0, candidate.get("cost", 0) / 2000)) * 0.3
            scored.append({**candidate, "score": round(score, 3)})
        return sorted(scored, key=lambda item: item["score"], reverse=True)


_location_scouting: LocationScouting | None = None


def get_location_scouting() -> LocationScouting:
    global _location_scouting
    if _location_scouting is None:
        _location_scouting = LocationScouting()
    return _location_scouting
