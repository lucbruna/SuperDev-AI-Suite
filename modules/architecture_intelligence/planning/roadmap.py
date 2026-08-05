"""Roadmap generator: a sequenced improvement plan from graph findings.

Consumes the deterministic insights and the graph structure to produce an
ordered list of improvement tasks with effort estimates and dependencies.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.dependency.orphan_detector import find_orphans
from modules.architecture_intelligence.reasoning.insight_engine import InsightEngine

_EFFORT = {"high": "L", "medium": "M", "low": "S"}


class RoadmapGenerator:
    """Builds a prioritized, sequenced roadmap."""

    def __init__(self) -> None:
        self.insights = InsightEngine()

    def generate(self, graph: Any) -> dict[str, Any]:
        findings = self.insights.run(graph, limit=20)
        tasks: list[dict[str, Any]] = []

        for finding in findings:
            tasks.append(
                {
                    "id": f"task-{len(tasks)}",
                    "action": finding["title"],
                    "detail": finding["recommendation"],
                    "severity": finding["severity"],
                    "effort": _EFFORT.get(finding["severity"], "M"),
                    "category": finding["category"],
                }
            )

        # Dead/orphan cleanup is cheap and independent: prefer it early.
        orphans = find_orphans(graph)
        if orphans and not any(t["category"] == "maintainability" for t in tasks):
            tasks.append(
                {
                    "id": f"task-{len(tasks)}",
                    "action": f"Review {len(orphans)} orphan file(s)",
                    "detail": "Wire, document or delete orphaned files.",
                    "severity": "medium",
                    "effort": "M",
                    "category": "maintainability",
                }
            )

        return {
            "summary": self._summary(tasks),
            "effort": self._effort_breakdown(tasks),
            "tasks": tasks,
            "total_tasks": len(tasks),
            "sequence": [t["id"] for t in tasks],
        }

    @staticmethod
    def _summary(tasks: list[dict[str, Any]]) -> str:
        if not tasks:
            return "No actionable improvements detected."
        priorities = [t for t in tasks if t["severity"] == "high"]
        if priorities:
            return f"{len(priorities)} high-priority item(s) to address first."
        return f"{len(tasks)} improvement item(s) queued."

    @staticmethod
    def _effort_breakdown(tasks: list[dict[str, Any]]) -> dict[str, int]:
        breakdown: dict[str, int] = {}
        for task in tasks:
            effort = task.get("effort", "M")
            breakdown[effort] = breakdown.get(effort, 0) + 1
        return breakdown


def generate_roadmap(graph: Any) -> dict[str, Any]:
    return RoadmapGenerator().generate(graph)
