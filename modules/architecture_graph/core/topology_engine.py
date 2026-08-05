"""Topology engine: layers, topological order and layering violations.

The platform follows a layered dependency rule (infrastructure < core < ai <
workflow_engine < runtime_engine < modules < backend < cli < frontend). This
engine detects when a lower layer imports from a higher layer — a structural
red flag for long-term maintainability.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import (
    ArchitectureGraph,
    layer_index,
    layer_of,
)


def assign_layers(graph: ArchitectureGraph) -> int:
    """Recompute node layers from paths. Returns the number of updates."""
    updated = 0
    for node in graph.nodes():
        layer = layer_of(node.path or node.name)
        if layer and layer != node.layer:
            node.layer = layer
            updated += 1
    return updated


def topological_order(
    graph: ArchitectureGraph, *, kind: str = "file"
) -> tuple[list[str], list[str]]:
    """Kahn's algorithm over dependency edges of the given node kind.

    Returns ``(ordered_ids, cycle_ids)``.
    """
    node_ids = [n.id for n in graph.nodes() if n.kind == kind]
    indegree: dict[str, int] = {nid: 0 for nid in node_ids}
    children: dict[str, list[str]] = {nid: [] for nid in node_ids}
    for edge in graph.edges():
        if edge.source not in indegree or edge.target not in indegree:
            continue
        indegree[edge.target] += 1
        children[edge.source].append(edge.target)

    queue = [nid for nid, deg in indegree.items() if deg == 0]
    ordered: list[str] = []
    while queue:
        current = queue.pop(0)
        ordered.append(current)
        for child in children[current]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    cycle_ids = [nid for nid in node_ids if indegree[nid] > 0]
    return ordered, cycle_ids


def layer_violations(graph: ArchitectureGraph) -> list[dict[str, Any]]:
    """Return dependency edges that cross layers in the wrong direction."""
    violations: list[dict[str, Any]] = []
    for edge in graph.edges():
        source = graph.get_node(edge.source)
        target = graph.get_node(edge.target)
        if source is None or target is None:
            continue
        if not source.layer or not target.layer:
            continue
        if source.layer == target.layer:
            continue
        if layer_index(source.layer) > layer_index(target.layer):
            violations.append(
                {
                    "source": edge.source,
                    "source_layer": source.layer,
                    "target": edge.target,
                    "target_layer": target.layer,
                    "kind": edge.kind,
                }
            )
    return violations


def layer_summary(graph: ArchitectureGraph) -> dict[str, int]:
    summary: dict[str, int] = {}
    for node in graph.nodes():
        key = node.layer or "unknown"
        summary[key] = summary.get(key, 0) + 1
    return summary
