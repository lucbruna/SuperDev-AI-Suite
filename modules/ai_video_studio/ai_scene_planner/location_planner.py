"""Location planner — suggest locations and settings for scenes."""
from __future__ import annotations

from typing import Any

LOCATIONS = {
    "generic": "neutral studio",
    "corporate": "modern office",
    "agriculture": "farm field",
    "education": "classroom",
    "healthcare": "clinic",
    "tourism": "landscape viewpoint",
    "tech": "laboratory",
    "finance": "boardroom",
    "retail": "storefront",
    "outdoor": "city park",
}

MOODS = ("bright", "warm", "cool", "dramatic", "neutral", "cozy")


class LocationPlanner:
    """Deterministic location suggestion based on brief keywords."""

    def plan(self, brief: str) -> dict[str, Any]:
        text = (brief or "").lower()
        location = "generic"
        for key, loc in LOCATIONS.items():
            if key != "generic" and key in text:
                location = loc
                break
        mood = MOODS[sum(ord(c) for c in text) % len(MOODS)] if text else "neutral"
        return {
            "location": location,
            "mood": mood,
            "interior": location not in ("farm field", "landscape viewpoint", "city park"),
            "time_of_day": "day",
            "notes": f"Recommended setting: {location} with a {mood} atmosphere.",
        }

    def list_locations(self) -> list[str]:
        return sorted(set(LOCATIONS.values()))


_location_planner: LocationPlanner | None = None


def get_location_planner() -> LocationPlanner:
    global _location_planner
    if _location_planner is None:
        _location_planner = LocationPlanner()
    return _location_planner
