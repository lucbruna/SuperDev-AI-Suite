"""Dependency report: markdown deep-dive into dependency health.

Focuses on dependency-level concerns: cycles, orphans, dead code, coupling
instability, top dependents/dependencies and the dependency score.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.analytics.coupling_analyzer import (
    coupling_metrics,
    hot_couples,
)
from modules.architecture_graph.analytics.dependency_score import dependency_health
from modules.architecture_graph.dependency.circular_detector import find_cycles
from modules.architecture_graph.dependency.dead_code_detector import (
    find_dead_files,
    summary as dead_summary,
)
from modules.architecture_graph.dependency.orphan_detector import (
    find_orphans,
    summary as orphan_summary,
)
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


class DependencyReport:
    """Build the markdown dependency report."""

    def generate(self, graph: ArchitectureGraph) -> str:
        cycles = find_cycles(graph)
        dead = find_dead_files(graph)
        orphans = find_orphans(graph)
        health = dependency_health(graph)
        coupling = coupling_metrics(graph)
        couples = hot_couples(graph, top=10)
        dead_s = dead_summary(dead)
        orphan_s = orphan_summary(orphans)

        lines = [
            "# Dependency Report",
            "",
            f"> Built at {graph.built_at}",
            "",
            "## Dependency Health",
            "",
            f"**Score:** {health.get('score', 0)} / 100 — grade **{health.get('grade', '?')}**",
            "",
            "## Cycles",
            "",
        ]
        if cycles:
            lines.append(f"**{len(cycles)} cycle(s)** detected:")
            lines.append("")
            for cycle in cycles[:10]:
                nodes = cycle.get("nodes", [])
                lines.append(f"- {len(nodes)} files: `{' -> '.join(nodes[:6])}{'…' if len(nodes) > 6 else ''}`")
        else:
            lines.append("_No cycles detected._")

        lines += [
            "",
            "## Dead Code & Orphans",
            "",
            f"- **Dead files:** {dead_s.get('files', 0)} "
            f"(+ {dead_s.get('packages', 0)} orphan packages)",
            f"- **Orphan files:** {orphan_s.get('total', 0)}",
            "",
        ]
        if orphans:
            lines.append("Top orphans by layer:")
            lines.append("")
            for layer, count in sorted(orphan_s.get("by_layer", {}).items(), key=lambda kv: -kv[1]):
                lines.append(f"- `{layer}`: {count}")
            lines.append("")

        lines += ["## Coupling", ""]
        for pkg in coupling.get("packages", [])[:10]:
            lines.append(
                f"- `{pkg['package']}` — instability {pkg.get('instability', 0):.2f} "
                f"(afferent {pkg.get('afferent', 0)}, efferent {pkg.get('efferent', 0)})"
            )

        lines += ["", "## Hottest dependency pairs", ""]
        for couple in couples:
            lines.append(f"- `{couple['source']}` → `{couple['target']}` ({couple['edges']} edges)")
        if not couples:
            lines.append("_No cross-package pairs found._")

        return "\n".join(lines) + "\n"

    def to_dict(self, graph: ArchitectureGraph) -> dict[str, Any]:
        return {
            "format": "markdown",
            "title": "Dependency Report",
            "source": self.generate(graph),
        }

    def write(self, graph: ArchitectureGraph, path: str) -> dict[str, Any]:
        from pathlib import Path

        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(self.generate(graph), encoding="utf-8")
        return {"path": str(dest), "bytes": dest.stat().st_size}


def dependency_report(graph: ArchitectureGraph) -> str:
    """One-shot convenience helper."""
    return DependencyReport().generate(graph)
