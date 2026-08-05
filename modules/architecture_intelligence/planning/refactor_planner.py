"""Refactor planner: concrete step-by-step refactor plans.

Given a set of target node ids (or the whole graph), produces a dependency-
aware sequence of refactor steps: break cycles first, then extract packages,
then migrate nodes into their target package.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.dependency.circular_detector import find_cycles


class RefactorPlanner:
    """Sequences refactor steps respecting dependency order."""

    def plan(
        self,
        graph: Any,
        *,
        targets: list[str] | None = None,
        target_package: str = "platform",
    ) -> dict[str, Any]:
        if targets:
            steps = [self._migrate_step(graph, node_id, target_package) for node_id in targets]
            return {
                "strategy": "migrate",
                "target_package": target_package,
                "steps": steps,
                "total": len(steps),
            }

        cycles = find_cycles(graph, kind="file")
        steps: list[dict[str, Any]] = []
        if cycles:
            steps.append(
                {
                    "order": 1,
                    "action": "break_cycles",
                    "detail": f"Break {len(cycles)} import cycle(s); extract shared cores first.",
                    "node_ids": [n for c in cycles for n in c.get("nodes", [])[:5]],
                }
            )
        hot_nodes = self._hot_nodes(graph)
        if hot_nodes:
            steps.append(
                {
                    "order": len(steps) + 1,
                    "action": "split_hotspots",
                    "detail": f"Split or slim down {len(hot_nodes)} high-complexity node(s).",
                    "node_ids": hot_nodes,
                }
            )
        steps.append(
            {
                "order": len(steps) + 1,
                "action": "consolidate",
                "detail": "Group cohesive files into modules and document package boundaries.",
                "node_ids": [],
            }
        )
        return {"strategy": "holistic", "steps": steps, "total": len(steps)}

    @staticmethod
    def _migrate_step(graph: Any, node_id: str, target_package: str) -> dict[str, Any]:
        node = graph.get_node(node_id) if graph.has_node(node_id) else None
        return {
            "node_id": node_id,
            "name": getattr(node, "name", node_id),
            "from_package": (getattr(node, "path", "") or "").split("/")[0] or "?",
            "to_package": target_package,
            "action": "migrate",
        }

    @staticmethod
    def _hot_nodes(graph: Any) -> list[str]:
        try:
            from modules.architecture_graph.analytics.complexity_analyzer import hotspots

            return [str(h.get("id", "")) for h in hotspots(graph, top=3) if h.get("id")]
        except Exception:
            return []


def refactor_plan(
    graph: Any, *, targets: list[str] | None = None, target_package: str = "platform"
) -> dict[str, Any]:
    return RefactorPlanner().plan(graph, targets=targets, target_package=target_package)
