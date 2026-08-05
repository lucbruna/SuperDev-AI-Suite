"""Insight engine: produces ranked, human-readable findings.

Uses the Architecture Graph analytics primitives (score, coupling, complexity,
dependency health, layer violations) to emit structured insights with a
severity, title, detail and recommendation. Purely heuristic — no LLM — so it
always works, and it feeds the LLM enrichment path when a provider exists.
"""
from __future__ import annotations

import threading
from typing import Any

from modules.architecture_graph.analytics.architecture_score import architecture_score
from modules.architecture_graph.analytics.complexity_analyzer import hotspots
from modules.architecture_graph.analytics.coupling_analyzer import hot_couples
from modules.architecture_graph.analytics.dependency_score import dependency_health
from modules.architecture_graph.core.integrity_engine import check as integrity_check
from modules.architecture_graph.core.topology_engine import (
    layer_violations,
    topological_order,
)
from modules.architecture_graph.dependency.circular_detector import find_cycles
from modules.architecture_graph.dependency.dead_code_detector import find_dead_files
from modules.architecture_graph.dependency.orphan_detector import find_orphans


class InsightEngine:
    """Deterministic insight extraction over an architecture graph."""

    def run(self, graph: Any, *, limit: int | None = None) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        self._cycles(graph, insights)
        self._violations(graph, insights)
        self._hotspots(graph, insights)
        self._couples(graph, insights)
        self._health(graph, insights)
        self._dead(graph, insights)
        self._orphans(graph, insights)
        self._score(graph, insights)
        insights.sort(key=lambda i: {"high": 0, "medium": 1, "low": 2}.get(i["severity"], 3))
        if limit:
            insights = insights[:limit]
        return insights

    # ------------------------------------------------------------ collectors
    def _cycles(self, graph: Any, out: list[dict[str, Any]]) -> None:
        cycles = find_cycles(graph, kind="file")
        if not cycles:
            return
        total = sum(c.get("size", 0) for c in cycles)
        out.append(
            {
                "id": f"cycles-{len(out)}",
                "severity": "high" if total > 10 else "medium",
                "category": "dependency",
                "title": f"{len(cycles)} import cycle(s) involving {total} files",
                "detail": "Cyclic dependencies make the graph harder to reason about and block clean layering.",
                "recommendation": "Break each cycle by extracting the shared core into a new package.",
                "data": {"cycles": len(cycles), "files": total},
            }
        )

    def _violations(self, graph: Any, out: list[dict[str, Any]]) -> None:
        violations = layer_violations(graph)
        if not violations:
            return
        out.append(
            {
                "id": f"violations-{len(out)}",
                "severity": "medium",
                "category": "layering",
                "title": f"{len(violations)} layer violation(s)",
                "detail": "Some edges point from a higher layer into a lower one.",
                "recommendation": "Move the offending dependency into the allowed direction or reclassify the layer.",
                "data": {"violations": len(violations)},
            }
        )

    def _hotspots(self, graph: Any, out: list[dict[str, Any]]) -> None:
        hot = hotspots(graph, top=5)
        if not hot:
            return
        names = ", ".join(str(h.get("id", "")) for h in hot[:3])
        out.append(
            {
                "id": f"hotspots-{len(out)}",
                "severity": "high",
                "category": "complexity",
                "title": f"{len(hot)} complexity hot spot(s): {names}",
                "detail": "These modules concentrate high complexity and risk.",
                "recommendation": "Split the largest hot spots or extract cohesive submodules.",
                "data": {"hotspots": hot},
            }
        )

    def _couples(self, graph: Any, out: list[dict[str, Any]]) -> None:
        couples = hot_couples(graph, top=3)
        if not couples:
            return
        strongest = couples[0]
        out.append(
            {
                "id": f"couples-{len(out)}",
                "severity": "medium",
                "category": "coupling",
                "title": f"Hot couple: {strongest.get('source')} ↔ {strongest.get('target')}",
                "detail": "A small set of packages accounts for many edges and can become a bottleneck.",
                "recommendation": "Consider splitting the hottest couples or introducing an abstraction between them.",
                "data": {"couples": couples},
            }
        )

    def _health(self, graph: Any, out: list[dict[str, Any]]) -> None:
        health = dependency_health(graph)
        ratio = health.get("healthy_ratio", 1.0)
        if ratio >= 0.8:
            return
        out.append(
            {
                "id": f"health-{len(out)}",
                "severity": "medium",
                "category": "dependency",
                "title": f"Dependency health is {ratio:.0%}",
                "detail": "A meaningful share of packages carries unstable dependency relationships.",
                "recommendation": "Stabilize the unstable packages or invert their dependencies.",
                "data": health,
            }
        )

    def _dead(self, graph: Any, out: list[dict[str, Any]]) -> None:
        dead = find_dead_files(graph)
        if not dead:
            return
        out.append(
            {
                "id": f"dead-{len(out)}",
                "severity": "low",
                "category": "maintainability",
                "title": f"{len(dead)} dead file(s) detected",
                "detail": "Files nobody imports may be dead weight.",
                "recommendation": "Verify and remove, or document each dead file.",
                "data": {"dead": len(dead)},
            }
        )

    def _orphans(self, graph: Any, out: list[dict[str, Any]]) -> None:
        orphans = find_orphans(graph)
        if not orphans:
            return
        out.append(
            {
                "id": f"orphans-{len(out)}",
                "severity": "medium",
                "category": "maintainability",
                "title": f"{len(orphans)} orphan file(s) not reachable from any entrypoint",
                "detail": "Orphaned files are not imported by anything and may be dead weight or missing references.",
                "recommendation": "Verify each orphan: delete if unused, otherwise wire it up or document the entrypoint.",
                "data": {"orphans": len(orphans)},
            }
        )

    def _score(self, graph: Any, out: list[dict[str, Any]]) -> None:
        score = architecture_score(graph)
        value = float(score.get("score", 0.0))
        if value >= 80:
            return
        out.append(
            {
                "id": f"score-{len(out)}",
                "severity": "medium" if value >= 60 else "high",
                "category": "quality",
                "title": f"Architecture score is {value:.1f}/100",
                "detail": "The overall score is below the 80-point bar.",
                "recommendation": "Address the weakest component (see score breakdown) first.",
                "data": {"score": score},
            }
        )


_insight_engine: InsightEngine | None = None
_lock = threading.Lock()


def get_insight_engine() -> InsightEngine:
    global _insight_engine
    if _insight_engine is None:
        with _lock:
            if _insight_engine is None:
                _insight_engine = InsightEngine()
    return _insight_engine


def insights(graph: Any, *, limit: int | None = None) -> list[dict[str, Any]]:
    return get_insight_engine().run(graph, limit=limit)
