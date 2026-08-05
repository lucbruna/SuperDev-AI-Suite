"""Planner reports — generate human-readable planning reports."""
from __future__ import annotations

from typing import Any


class PlannerReports:
    """Generates text/JSON reports from a scene plan."""

    def summary(self, scenes: list[dict[str, Any]]) -> dict[str, Any]:
        total = sum(s.get("duration", 0) for s in scenes)
        types: dict[str, int] = {}
        for s in scenes:
            t = s.get("scene_type", "content")
            types[t] = types.get(t, 0) + 1
        return {
            "scene_count": len(scenes),
            "total_duration": round(total, 3),
            "scene_types": types,
            "avg_duration": round(total / len(scenes), 3) if scenes else 0.0,
        }

    def to_markdown(self, scenes: list[dict[str, Any]]) -> str:
        lines = ["# Scene Plan", ""]
        for s in scenes:
            lines.append(f"## Scene {s.get('index', 0) + 1}: {s.get('name', 'Untitled')}")
            lines.append(f"- Type: {s.get('scene_type', 'content')}")
            lines.append(f"- Duration: {s.get('duration', 0)}s")
            desc = s.get("description")
            if desc:
                lines.append(f"- Description: {desc}")
            lines.append("")
        return "\n".join(lines)

    def to_json(self, scenes: list[dict[str, Any]]) -> dict[str, Any]:
        return {"summary": self.summary(scenes), "scenes": scenes}


_planner_reports: PlannerReports | None = None


def get_planner_reports() -> PlannerReports:
    global _planner_reports
    if _planner_reports is None:
        _planner_reports = PlannerReports()
    return _planner_reports
