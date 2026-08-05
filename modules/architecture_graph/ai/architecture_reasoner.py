"""Architecture reasoning: turn raw graph signals into human insights.

Combines the analysis engines (cycles, orphans, dead code, layer violations,
coupling, impact) with the graph structure to produce ranked, explainable
insights and recommendations.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.analytics.coupling_analyzer import coupling_metrics
from modules.architecture_graph.analytics.complexity_analyzer import hotspots as complexity_hotspots
from modules.architecture_graph.core.impact_engine import risk_score
from modules.architecture_graph.core.integrity_engine import check as integrity_check
from modules.architecture_graph.core.metrics_engine import graph_metrics
from modules.architecture_graph.core.topology_engine import layer_violations
from modules.architecture_graph.dependency.circular_detector import find_cycles
from modules.architecture_graph.dependency.dead_code_detector import find_dead_files
from modules.architecture_graph.dependency.orphan_detector import find_orphans
from modules.architecture_graph.dependency.unused_plugin_detector import (
    find_unused_plugins,
)
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


class ArchitectureReasoner:
    """Produces ranked insights and natural-language recommendations."""

    # Each detector contributes (severity, title, detail, recommendation).
    def analyze(self, graph: ArchitectureGraph) -> dict[str, Any]:
        """Run every detector and assemble a consolidated insight report."""
        insights: list[dict[str, Any]] = []
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        cycles = find_cycles(graph)
        if cycles:
            involved = sorted({n for c in cycles for n in c.get("nodes", [])})
            insights.append(
                {
                    "severity": "critical",
                    "category": "cycles",
                    "title": f"{len(cycles)} dependency cycle(s) detected",
                    "detail": f"Cycles involve {len(involved)} files. Cyclic "
                    "dependencies block clean layering and incremental builds.",
                    "nodes": involved[:20],
                    "recommendation": "Break the cycles by extracting shared code "
                    "into a lower-level package that both sides depend on.",
                }
            )

        orphans = find_orphans(graph)
        if orphans:
            insights.append(
                {
                    "severity": "high",
                    "category": "orphans",
                    "title": f"{len(orphans)} orphan file(s) not reachable from any entrypoint",
                    "detail": "Orphaned files are not imported by anything and may "
                    "be dead weight or missing references.",
                    "nodes": orphans[:20],
                    "recommendation": "Verify each orphan: delete if unused, "
                    "otherwise wire it up or document the entrypoint.",
                }
            )

        dead = find_dead_files(graph)
        if dead:
            insights.append(
                {
                    "severity": "high",
                    "category": "dead_code",
                    "title": f"{len(dead)} dead file(s) (no dependents)",
                    "detail": "Files nobody depends on and which do not declare an "
                    "entrypoint marker.",
                    "nodes": dead[:20],
                    "recommendation": "Review and remove dead files to reduce "
                    "maintenance surface.",
                }
            )

        violations = layer_violations(graph)
        if violations:
            insights.append(
                {
                    "severity": "medium",
                    "category": "layer_violations",
                    "title": f"{len(violations)} layer violation(s)",
                    "detail": "Dependencies point from an upper layer into a lower "
                    "layer that the source does not depend on.",
                    "nodes": [v.get("source", "") for v in violations[:20]],
                    "recommendation": "Restructure the violating edges or document "
                    "the intentional exception.",
                }
            )

        unused = find_unused_plugins(graph)
        if unused:
            insights.append(
                {
                    "severity": "medium",
                    "category": "unused_plugins",
                    "title": f"{len(unused)} unused plugin(s)",
                    "detail": "Declared plugins that never appear in workflows.",
                    "nodes": [p.get("id", "") for p in unused[:20]],
                    "recommendation": "Uninstall or wire the unused plugins into "
                    "the workflows that need them.",
                }
            )

        issues = integrity_check(graph)
        if issues:
            kinds: dict[str, int] = {}
            for issue in issues:
                kinds[issue.get("type", "?")] = kinds.get(issue.get("type", "?"), 0) + 1
            insights.append(
                {
                    "severity": "low",
                    "category": "integrity",
                    "title": f"{len(issues)} integrity issue(s)",
                    "detail": ", ".join(f"{k}: {v}" for k, v in sorted(kinds.items())),
                    "nodes": [],
                    "recommendation": "Fix the listed integrity issues to keep the "
                    "graph consistent.",
                }
            )

        coupling = coupling_metrics(graph)
        hot = [p for p in coupling.get("packages", []) if p.get("instability", 0) >= 0.8][:5]
        if hot:
            insights.append(
                {
                    "severity": "low",
                    "category": "coupling",
                    "title": f"{len(hot)} unstable package(s)",
                    "detail": "Packages with instability >= 0.8 (depend on many "
                    "packages while few depend on them).",
                    "nodes": [h.get("package", "") for h in hot],
                    "recommendation": "Consider splitting the most unstable packages "
                    "into smaller cohesive units.",
                }
            )

        insights.sort(key=lambda i: severity_order.get(i["severity"], 9))
        return {
            "count": len(insights),
            "by_severity": {
                level: sum(1 for i in insights if i["severity"] == level)
                for level in ("critical", "high", "medium", "low")
            },
            "insights": insights,
            "metrics": graph_metrics(graph),
        }

    def risk_ranking(self, graph: ArchitectureGraph, *, limit: int = 10) -> list[dict[str, Any]]:
        """Rank the highest-risk nodes in the graph."""
        scored: list[tuple[float, str]] = []
        for node in graph.nodes():
            if node.kind not in {"file", "module", "package", "api"}:
                continue
            try:
                result = risk_score(graph, node.id)
            except Exception:
                continue
            scored.append((result.get("risk", 0.0), node.id))
        scored.sort(reverse=True)
        top: list[dict[str, Any]] = []
        for score, node_id in scored[:limit]:
            node = graph.get_node(node_id)
            top.append(
                {
                    "node_id": node_id,
                    "name": node.name if node else node_id,
                    "kind": node.kind if node else "",
                    "risk": round(score, 3),
                }
            )
        return top


def reason(graph: ArchitectureGraph) -> dict[str, Any]:
    """One-shot convenience helper."""
    return ArchitectureReasoner().analyze(graph)
