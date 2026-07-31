"""Impact analysis."""

from __future__ import annotations

from typing import Any


class ImpactAnalyzer:
    def __init__(self) -> None:
        self._analyses: list[dict[str, Any]] = []

    def analyze(self, change: dict[str, Any], affected_areas: list[str]) -> dict[str, Any]:
        impacts = {}
        for area in affected_areas:
            impacts[area] = {"severity": "medium", "probability": 0.6, "estimated_impact": 0.3}
        result = {
            "change": change,
            "impacts": impacts,
            "total_areas": len(affected_areas),
            "overall_impact": sum(i["estimated_impact"] for i in impacts.values()) / len(impacts) if impacts else 0,
        }
        self._analyses.append(result)
        return result

    def cascade(self, initial_impact: dict[str, Any], dependencies: dict[str, list[str]]) -> dict[str, Any]:
        cascade_effects = []
        visited = set()
        queue = list(initial_impact.get("affected_areas", []))
        while queue:
            area = queue.pop(0)
            if area in visited:
                continue
            visited.add(area)
            cascade_effects.append({"area": area, "level": len(cascade_effects)})
            queue.extend(dependencies.get(area, []))
        return {"cascade": cascade_effects, "total_affected": len(cascade_effects)}

    def get_analyses(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._analyses[-limit:]

    def count(self) -> int:
        return len(self._analyses)
