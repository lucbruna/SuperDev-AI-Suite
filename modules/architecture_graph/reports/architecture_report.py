"""Architecture report: markdown summary of the whole platform health.

Combines the score, metrics, issues, risks and plan into a single
human-readable report for stakeholders and engineers.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.analytics.architecture_score import architecture_score
from modules.architecture_graph.ai.architecture_planner import ArchitecturePlanner
from modules.architecture_graph.ai.architecture_reasoner import ArchitectureReasoner
from modules.architecture_graph.core.metrics_engine import graph_metrics
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


class ArchitectureReport:
    """Build the canonical markdown architecture report."""

    def generate(self, graph: ArchitectureGraph) -> str:
        score = architecture_score(graph)
        metrics = graph_metrics(graph)
        insights = ArchitectureReasoner().analyze(graph)
        plan = ArchitecturePlanner().plan(graph)

        lines = [
            f"# Architecture Report — {graph.name}",
            "",
            f"> Built at {graph.built_at} · project root: `{graph.project_root or '—'}`",
            "",
            "## Overall Score",
            "",
            f"**{score.get('score', 0)} / 100** — grade **{score.get('grade', '?')}**",
            "",
            "| Component | Score |",
            "| --- | --- |",
        ]
        for component, value in score.get("components", {}).items():
            lines.append(f"| {component} | {value} |")

        lines += [
            "",
            "## Metrics",
            "",
            f"- Nodes: {metrics.get('nodes', 0)}",
            f"- Edges: {metrics.get('edges', 0)}",
            f"- Density: {metrics.get('density', 0):.3f}",
            f"- Connected components: {metrics.get('connected_components', 0)}",
            "",
            "## Insights",
            "",
        ]
        for insight in insights.get("insights", []):
            lines.append(f"### [{insight['severity'].upper()}] {insight['title']}")
            lines.append("")
            lines.append(insight.get("detail", ""))
            lines.append("")
            lines.append(f"**Recommendation:** {insight.get('recommendation', '—')}")
            lines.append("")

        lines += ["## Improvement Plan", ""]
        for task in plan.get("tasks", [])[:20]:
            lines.append(f"- `[{task['effort']}]` {task['title']}")
        if not plan.get("tasks"):
            lines.append("_No improvement tasks detected — the architecture is clean._")

        return "\n".join(lines) + "\n"

    def to_dict(self, graph: ArchitectureGraph) -> dict[str, Any]:
        return {
            "format": "markdown",
            "title": f"Architecture Report — {graph.name}",
            "source": self.generate(graph),
        }

    def write(self, graph: ArchitectureGraph, path: str) -> dict[str, Any]:
        from pathlib import Path

        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(self.generate(graph), encoding="utf-8")
        return {"path": str(dest), "bytes": dest.stat().st_size}


def architecture_report(graph: ArchitectureGraph) -> str:
    """One-shot convenience helper."""
    return ArchitectureReport().generate(graph)
