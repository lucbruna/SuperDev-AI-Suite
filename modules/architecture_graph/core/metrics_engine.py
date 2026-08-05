"""Metrics engine: fan-in/fan-out, coupling, density and aggregation."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def node_metrics(graph: ArchitectureGraph, node_id: str) -> dict[str, Any]:
    node = graph.get_node(node_id)
    if node is None:
        return {}
    incoming = graph.incoming(node_id)
    outgoing = graph.outgoing(node_id)
    return {
        "id": node_id,
        "name": node.name,
        "kind": node.kind,
        "layer": node.layer,
        "fan_in": len(incoming),
        "fan_out": len(outgoing),
        "coupling": len(incoming) + len(outgoing),
        "dependents": incoming,
        "dependencies": outgoing,
    }


def graph_metrics(graph: ArchitectureGraph) -> dict[str, Any]:
    """Aggregate metrics over the whole graph."""
    nodes = graph.node_ids()
    n = len(nodes)
    edge_count = len(graph.edges())
    density = 0.0
    if n > 1:
        density = edge_count / (n * (n - 1))
    total_fan_in = 0
    max_fan_in: tuple[str, int] = ("", 0)
    total_fan_out = 0
    max_fan_out: tuple[str, int] = ("", 0)
    for node_id in nodes:
        fin = len(graph.incoming(node_id))
        fout = len(graph.outgoing(node_id))
        total_fan_in += fin
        total_fan_out += fout
        if fin > max_fan_in[1]:
            max_fan_in = (node_id, fin)
        if fout > max_fan_out[1]:
            max_fan_out = (node_id, fout)

    components = _connected_components(graph)
    return {
        "nodes": n,
        "edges": edge_count,
        "density": round(density, 6),
        "avg_fan_in": round(total_fan_in / n, 3) if n else 0.0,
        "avg_fan_out": round(total_fan_out / n, 3) if n else 0.0,
        "max_fan_in_node": max_fan_in[0],
        "max_fan_in": max_fan_in[1],
        "max_fan_out_node": max_fan_out[0],
        "max_fan_out": max_fan_out[1],
        "connected_components": components,
    }


def _connected_components(graph: ArchitectureGraph) -> int:
    seen: set[str] = set()
    components = 0
    for node_id in graph.node_ids():
        if node_id in seen:
            continue
        components += 1
        stack = [node_id]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(graph.neighbors(current))
    return components


def module_metrics(graph: ArchitectureGraph) -> list[dict[str, Any]]:
    """Aggregate metrics per top-level directory (package/module layer)."""
    agg: dict[str, dict[str, Any]] = {}
    for node in graph.nodes():
        parts = (node.path or node.name).replace("\\", "/").split("/")
        top = parts[0] if parts else "?"
        bucket = agg.setdefault(
            top,
            {"module": top, "files": 0, "nodes": 0, "edges": 0, "fan_in": 0, "fan_out": 0},
        )
        bucket["nodes"] += 1
        if node.kind == "file":
            bucket["files"] += 1
        bucket["fan_in"] += len(graph.incoming(node.id))
        bucket["fan_out"] += len(graph.outgoing(node.id))
    for bucket in agg.values():
        bucket["coupling"] = bucket["fan_in"] + bucket["fan_out"]
    return sorted(agg.values(), key=lambda b: b["coupling"], reverse=True)
