"""Architecture planning: build actionable refactoring/migration plans.

Turns the detected issues (cycles, orphans, dead code, layer violations,
high-risk nodes) into ordered, dependency-aware work items with estimated
effort and a suggested execution order.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.ai.architecture_reasoner import ArchitectureReasoner
from modules.architecture_graph.core.topology_engine import topological_order
from modules.architecture_graph.dependency.circular_detector import find_cycles
from modules.architecture_graph.dependency.dead_code_detector import find_dead_files
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


class ArchitecturePlanner:
    """Generates and sequences architecture improvement tasks."""

    # Rough effort buckets per work item type.
    _EFFORT = {
        "remove_dead_code": "S",
        "document_node": "S",
        "fix_integrity": "S",
        "break_cycle": "L",
        "move_layer": "M",
        "split_module": "XL",
        "add_entrypoint": "M",
    }

    def plan(self, graph: ArchitectureGraph) -> dict[str, Any]:
        """Full improvement plan derived from the current graph state."""
        tasks: list[dict[str, Any]] = []

        reasoner = ArchitectureReasoner()
        report = reasoner.analyze(graph)
        cycles = find_cycles(graph)
        dead = find_dead_files(graph)

        # 1) Dead code removal is cheap and low-risk.
        for item in dead[:25]:
            tasks.append(
                self._task(
                    node_id=item["id"],
                    action="remove_dead_code",
                    title=f"Remove dead file {item['id']}",
                    detail="No dependents and no declared entrypoint.",
                )
            )

        # 2) Cycle breaking requires a dependency chain, hence 'L'.
        for cycle in cycles:
            nodes = cycle.get("nodes", [])
            if not nodes:
                continue
            representative = nodes[0]
            tasks.append(
                self._task(
                    node_id=representative,
                    action="break_cycle",
                    title=f"Break dependency cycle of {len(nodes)} files",
                    detail=f"Cycle: {' -> '.join(nodes[:5])}{'...' if len(nodes) > 5 else ''}",
                )
            )

        # 3) Layer violations.
        violations = report.get("insights", [])
        for insight in violations:
            if insight.get("category") != "layer_violations":
                continue
            nodes = insight.get("nodes", [])
            for node_id in nodes[:10]:
                tasks.append(
                    self._task(
                        node_id=node_id,
                        action="move_layer",
                        title=f"Resolve layer violation at {node_id}",
                        detail=insight.get("detail", ""),
                    )
                )

        # 4) Top risk nodes -> splitting advice.
        for item in reasoner.risk_ranking(graph, limit=5):
            node_id = item["node_id"]
            if item.get("risk", 0) < 0.5:
                continue
            tasks.append(
                self._task(
                    node_id=node_id,
                    action="split_module",
                    title=f"Reduce blast radius of {item['name']}",
                    detail=f"Risk {item['risk']:.2f}; split into cohesive units.",
                )
            )

        # 5) Orphans reachable from no entrypoint.
        from modules.architecture_graph.dependency.orphan_detector import find_orphans

        for item in find_orphans(graph)[:15]:
            tasks.append(
                self._task(
                    node_id=item["id"],
                    action="add_entrypoint",
                    title=f"Wire or document orphan {item['id']}",
                    detail="Not reachable from any declared entrypoint.",
                )
            )

        # Order tasks: removal first, then cycles (blocking), then rest.
        order = {"remove_dead_code": 0, "fix_integrity": 1, "break_cycle": 2,
                 "add_entrypoint": 3, "move_layer": 4, "split_module": 5,
                 "document_node": 6}
        tasks.sort(key=lambda t: (order.get(t["action"], 9), t["node_id"]))

        effort_counts: dict[str, int] = {}
        for task in tasks:
            effort_counts[task["effort"]] = effort_counts.get(task["effort"], 0) + 1

        return {
            "total_tasks": len(tasks),
            "effort": effort_counts,
            "estimated_sequence": self._sequence(tasks),
            "tasks": tasks,
        }

    def _sequence(self, tasks: list[dict[str, Any]]) -> list[str]:
        """Compact execution sequence summary."""
        if not tasks:
            return []
        seen: set[str] = set()
        sequence: list[str] = []
        for task in tasks:
            action = task["action"]
            if action not in seen:
                seen.add(action)
                sequence.append(action)
        return sequence

    @staticmethod
    def _task(node_id: str, action: str, title: str, detail: str) -> dict[str, Any]:
        return {
            "node_id": node_id,
            "action": action,
            "title": title,
            "detail": detail,
            "effort": ArchitecturePlanner._EFFORT.get(action, "M"),
        }

    def migration_plan(
        self,
        graph: ArchitectureGraph,
        *,
        target_package: str,
        nodes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Plan a migration of nodes into a target package, dependency-aware."""
        ordered, _ = topological_order(graph, kind="file")
        candidates = nodes or ordered
        steps: list[dict[str, Any]] = []
        for node_id in candidates:
            node = graph.get_node(node_id)
            if node is None:
                continue
            dependents = graph.incoming(node_id)
            steps.append(
                {
                    "node_id": node_id,
                    "name": node.name,
                    "from_package": node.path.split("/")[0] if node.path else "",
                    "to_package": target_package,
                    "blocked_by": dependents[:10],
                    "order_hint": "migrate dependents first"
                    if dependents
                    else "safe to move",
                }
            )
        return {
            "target_package": target_package,
            "total": len(steps),
            "migrate_first": [s for s in steps if not s["blocked_by"]][:10],
            "steps": steps,
        }


def plan(graph: ArchitectureGraph) -> dict[str, Any]:
    """One-shot convenience helper."""
    return ArchitecturePlanner().plan(graph)
