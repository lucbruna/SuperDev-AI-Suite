"""Complexity analyzer: heuristic complexity per node.

Without full AST analysis of every language, complexity is approximated from
structural signals available in the graph: size, fan-out (dependencies) and
fan-in (dependents). High complexity + high fan-in marks a change hotspot.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def _complexity(size: int, fan_in: int, fan_out: int) -> float:
    size_component = min(size / 400.0, 1.0)          # >400 lines -> max
    fan_out_component = min(fan_out / 30.0, 1.0)     # >30 deps -> max
    fan_in_component = min(fan_in / 40.0, 1.0)       # >40 dependents -> max
    return round(0.5 * size_component + 0.3 * fan_out_component + 0.2 * fan_in_component, 3)


def complexity_scores(
    graph: ArchitectureGraph, *, top: int = 50, min_size: int = 0
) -> list[dict[str, Any]]:
    scores: list[dict[str, Any]] = []
    for node in graph.nodes():
        if node.kind not in {"file", "module", "package"}:
            continue
        if node.size < min_size:
            continue
        fan_in = len(graph.incoming(node.id))
        fan_out = len(graph.outgoing(node.id))
        scores.append(
            {
                "id": node.id,
                "name": node.name,
                "path": node.path,
                "kind": node.kind,
                "size": node.size,
                "fan_in": fan_in,
                "fan_out": fan_out,
                "complexity": _complexity(node.size, fan_in, fan_out),
            }
        )
    scores.sort(key=lambda s: s["complexity"], reverse=True)
    return scores[:top]


def hotspots(graph: ArchitectureGraph, top: int = 20) -> list[dict[str, Any]]:
    """High complexity AND high fan-in -> risky change targets."""
    all_scores = complexity_scores(graph, top=max(top * 5, 50))
    hotspots_list = [
        s for s in all_scores if s["complexity"] >= 0.5 and s["fan_in"] >= 3
    ][:top]
    return hotspots_list
