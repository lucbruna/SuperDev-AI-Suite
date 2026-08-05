"""Impact engine: what breaks if a node changes.

Walks the reverse dependency graph (dependents) up to a configurable depth
and scores the blast radius of a change.
"""
from __future__ import annotations

from collections import deque
from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def dependents(
    graph: ArchitectureGraph, node_id: str, max_depth: int = 12
) -> dict[str, Any]:
    """All transitive dependents of a node with their distance."""
    if not graph.has_node(node_id):
        return {"node_id": node_id, "found": False, "impacted": [], "total": 0, "max_depth": 0}

    depth: dict[str, int] = {node_id: 0}
    queue: deque[str] = deque([node_id])
    impacted: list[dict[str, Any]] = []
    while queue:
        current = queue.popleft()
        for dependent in graph.incoming(current):
            if dependent in depth:
                continue
            d = depth[current] + 1
            if d > max_depth:
                continue
            depth[dependent] = d
            queue.append(dependent)
            node = graph.get_node(dependent)
            impacted.append(
                {
                    "id": dependent,
                    "name": node.name if node else dependent,
                    "kind": node.kind if node else "",
                    "path": node.path if node else "",
                    "depth": d,
                }
            )

    impacted.sort(key=lambda item: (item["depth"], item["id"]))
    return {
        "node_id": node_id,
        "found": True,
        "impacted": impacted,
        "total": len(impacted),
        "max_depth": max(depth.values()) if depth else 0,
    }


def dependencies(
    graph: ArchitectureGraph, node_id: str, max_depth: int = 12
) -> dict[str, Any]:
    """All transitive dependencies of a node (what it needs)."""
    if not graph.has_node(node_id):
        return {"node_id": node_id, "found": False, "dependencies": [], "total": 0}

    depth: dict[str, int] = {node_id: 0}
    queue: deque[str] = deque([node_id])
    result: list[dict[str, Any]] = []
    while queue:
        current = queue.popleft()
        for dependency in graph.outgoing(current):
            if dependency in depth:
                continue
            d = depth[current] + 1
            if d > max_depth:
                continue
            depth[dependency] = d
            queue.append(dependency)
            node = graph.get_node(dependency)
            result.append(
                {
                    "id": dependency,
                    "name": node.name if node else dependency,
                    "kind": node.kind if node else "",
                    "path": node.path if node else "",
                    "depth": d,
                }
            )
    result.sort(key=lambda item: (item["depth"], item["id"]))
    return {
        "node_id": node_id,
        "found": True,
        "dependencies": result,
        "total": len(result),
    }


def risk_score(graph: ArchitectureGraph, node_id: str, max_depth: int = 12) -> dict[str, Any]:
    """Blast-radius risk: 0 (isolated) .. 1 (touches almost everything)."""
    impact = dependents(graph, node_id, max_depth)
    total_nodes = max(1, len(graph))
    direct = len(graph.incoming(node_id))
    fan_out = len(graph.outgoing(node_id))
    depth_factor = min(impact.get("max_depth", 0) / max(1, max_depth), 1.0)

    if not impact.get("found", False):
        return {"node_id": node_id, "risk": 0.0, "reason": "not found"}

    size_factor = min(impact["total"] / total_nodes, 1.0)
    coupling_factor = min((direct + fan_out) / 50.0, 1.0)
    risk = round(0.6 * size_factor + 0.25 * coupling_factor + 0.15 * depth_factor, 3)
    return {
        "node_id": node_id,
        "risk": risk,
        "impacted": impact["total"],
        "total_nodes": total_nodes,
        "direct_dependents": direct,
        "fan_out": fan_out,
        "reason": (
            "high" if risk >= 0.6 else "medium" if risk >= 0.3 else "low"
        ),
    }
