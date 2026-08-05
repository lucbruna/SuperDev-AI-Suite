"""Circular dependency detector (Tarjan's strongly connected components)."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def find_cycles(
    graph: ArchitectureGraph, *, kind: str = "file"
) -> list[dict[str, Any]]:
    """Return strongly connected components with more than one node
    (true dependency cycles), plus self-loops."""
    node_ids = [n.id for n in graph.nodes() if n.kind == kind]
    index: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    counter = [0]
    sccs: list[list[str]] = []

    def strongconnect(node_id: str) -> None:
        index[node_id] = lowlink[node_id] = counter[0]
        counter[0] += 1
        stack.append(node_id)
        on_stack.add(node_id)
        for neighbor in graph.outgoing(node_id):
            if neighbor not in node_ids:
                continue
            if neighbor not in index:
                strongconnect(neighbor)
                lowlink[node_id] = min(lowlink[node_id], lowlink[neighbor])
            elif neighbor in on_stack:
                lowlink[node_id] = min(lowlink[node_id], index[neighbor])
        if lowlink[node_id] == index[node_id]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.discard(member)
                component.append(member)
                if member == node_id:
                    break
            if len(component) > 1:
                sccs.append(sorted(component))

    for node_id in node_ids:
        if node_id not in index:
            strongconnect(node_id)

    cycles: list[dict[str, Any]] = []
    for component in sccs:
        member_set = set(component)
        edges = [
            {
                "source": e.source,
                "target": e.target,
                "kind": e.kind,
            }
            for e in graph.edges()
            if e.source in member_set and e.target in member_set
        ]
        cycles.append(
            {
                "size": len(component),
                "nodes": component,
                "edges": edges,
            }
        )
    cycles.sort(key=lambda c: c["size"], reverse=True)
    return cycles


def summary(cycles: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total": len(cycles),
        "largest": max((c["size"] for c in cycles), default=0),
        "involved_nodes": sum(c["size"] for c in cycles),
    }
