"""Continuity engine — verify continuity across scenes and shots."""
from __future__ import annotations

from typing import Any


class ContinuityEngine:
    """Checks continuity: consistent characters, locations, lighting, props."""

    def check(self, scenes: list[dict[str, Any]]) -> dict[str, Any]:
        issues: list[str] = []
        locations: set[str] = set()
        characters: set[str] = set()
        lighting: set[str] = set()

        for scene in scenes:
            loc = scene.get("location") or scene.get("environment")
            if loc:
                locations.add(loc)
            char = scene.get("character")
            if char:
                characters.add(char)
            light = scene.get("lighting") or scene.get("mood")
            if light:
                lighting.add(light)

        if len(locations) > 1:
            issues.append(f"Multiple locations without transition: {', '.join(sorted(locations))}")
        if len(characters) > 1:
            issues.append(f"Multiple characters without explanation: {', '.join(sorted(characters))}")
        if len(lighting) > 1:
            issues.append(f"Inconsistent lighting across scenes: {', '.join(sorted(lighting))}")

        return {
            "consistent": not issues,
            "issues": issues,
            "locations": sorted(locations),
            "characters": sorted(characters),
            "lighting": sorted(lighting),
        }

    def verify_shot_continuity(self, shots: list[dict[str, Any]]) -> dict[str, Any]:
        issues: list[str] = []
        for i in range(1, len(shots)):
            prev, cur = shots[i - 1], shots[i]
            if prev.get("subject") != cur.get("subject"):
                issues.append(f"Subject changed between shot {i} and {i + 1}")
        return {"consistent": not issues, "issues": issues}


_continuity_engine: ContinuityEngine | None = None


def get_continuity_engine() -> ContinuityEngine:
    global _continuity_engine
    if _continuity_engine is None:
        _continuity_engine = ContinuityEngine()
    return _continuity_engine
