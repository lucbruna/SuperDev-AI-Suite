"""Dependency score: health of dependency relationships (0..100)."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.dependency.circular_detector import find_cycles
from modules.architecture_graph.dependency.orphan_detector import find_orphans
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def dependency_health(graph: ArchitectureGraph) -> dict[str, Any]:
    cycles = find_cycles(graph)
    orphans = find_orphans(graph)
    total_files = sum(1 for n in graph.nodes() if n.kind == "file")

    cycle_penalty = min(sum(c["size"] for c in cycles) / max(1, total_files), 1.0)
    orphan_penalty = min(len(orphans) / max(1, total_files), 1.0)

    score = round(100.0 * (1.0 - 0.7 * cycle_penalty - 0.3 * orphan_penalty), 1)
    return {
        "score": max(0.0, score),
        "total_files": total_files,
        "cycles": len(cycles),
        "cycle_nodes": sum(c["size"] for c in cycles),
        "orphans": len(orphans),
        "grade": _grade(score),
    }


def _grade(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"
