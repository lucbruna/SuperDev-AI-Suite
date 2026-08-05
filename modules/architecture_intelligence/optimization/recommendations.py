"""Optimizer: actionable, prioritized optimization recommendations.

Derives recommendations from the graph analytics (score components, coupling,
complexity, dead code) with clear actions and estimated impact.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.analytics.architecture_score import architecture_score
from modules.architecture_graph.analytics.complexity_analyzer import hotspots
from modules.architecture_graph.analytics.coupling_analyzer import coupling_metrics
from modules.architecture_graph.dependency.dead_code_detector import find_dead_files
from modules.architecture_graph.dependency.orphan_detector import find_orphans


class Optimizer:
    """Builds a recommendation list ranked by impact."""

    def recommend(self, graph: Any, *, limit: int | None = None) -> dict[str, Any]:
        recommendations: list[dict[str, Any]] = []
        self._score_drivers(graph, recommendations)
        self._coupling(graph, recommendations)
        self._complexity(graph, recommendations)
        self._dead_code(graph, recommendations)
        self._orphans(graph, recommendations)
        recommendations.sort(
            key=lambda r: {"high": 0, "medium": 1, "low": 2}.get(r.get("priority", "low"), 3)
        )
        if limit:
            recommendations = recommendations[:limit]
        return {
            "format": "recommendations",
            "total": len(recommendations),
            "recommendations": recommendations,
        }

    def _score_drivers(self, graph: Any, out: list[dict[str, Any]]) -> None:
        score = architecture_score(graph)
        value = float(score.get("score", 0.0))
        breakdown = score.get("breakdown") or score.get("components") or {}
        if value >= 80:
            return
        weakest = min(breakdown.items(), key=lambda kv: kv[1]) if breakdown else None
        out.append(
            {
                "id": f"opt-score",
                "priority": "high" if value < 60 else "medium",
                "category": "quality",
                "action": f"Improve {weakest[0] if weakest else 'overall'} component",
                "detail": f"Current score {value:.1f}/100; weakest component is "
                f"'{weakest[0]}' ({weakest[1]:.1f})." if weakest else f"Current score {value:.1f}/100.",
                "impact": "score",
                "data": {"score": score},
            }
        )

    def _coupling(self, graph: Any, out: list[dict[str, Any]]) -> None:
        metrics = coupling_metrics(graph)
        total = metrics.get("total", 0)
        unstable = [p for p in metrics.get("packages", []) if p.get("instability", 1.0) >= 0.8]
        if not unstable:
            return
        out.append(
            {
                "id": f"opt-coupling",
                "priority": "medium",
                "category": "coupling",
                "action": f"Stabilize {len(unstable)} unstable package(s)",
                "detail": f"Packages with instability >= 0.8: "
                f"{', '.join(str(p.get('name', '?')) for p in unstable[:5])}.",
                "impact": "coupling",
                "data": {"total": total, "unstable": len(unstable)},
            }
        )

    def _complexity(self, graph: Any, out: list[dict[str, Any]]) -> None:
        hot = hotspots(graph, top=3)
        if not hot:
            return
        out.append(
            {
                "id": f"opt-complexity",
                "priority": "medium",
                "category": "complexity",
                "action": f"Reduce complexity in {len(hot)} hot spot(s)",
                "detail": "High-complexity modules concentrate defect risk.",
                "impact": "maintainability",
                "data": {"hotspots": hot},
            }
        )

    def _dead_code(self, graph: Any, out: list[dict[str, Any]]) -> None:
        dead = find_dead_files(graph)
        if not dead:
            return
        out.append(
            {
                "id": f"opt-dead",
                "priority": "low",
                "category": "maintainability",
                "action": f"Remove or document {len(dead)} dead file(s)",
                "detail": "Files without dependents are dead weight.",
                "impact": "maintainability",
                "data": {"dead": len(dead)},
            }
        )

    def _orphans(self, graph: Any, out: list[dict[str, Any]]) -> None:
        orphans = find_orphans(graph)
        if not orphans:
            return
        out.append(
            {
                "id": f"opt-orphans",
                "priority": "medium",
                "category": "maintainability",
                "action": f"Wire up {len(orphans)} orphan file(s)",
                "detail": "Orphans are not reachable from any entrypoint.",
                "impact": "maintainability",
                "data": {"orphans": len(orphans)},
            }
        )


def optimize(graph: Any, *, limit: int | None = None) -> dict[str, Any]:
    return Optimizer().recommend(graph, limit=limit)
