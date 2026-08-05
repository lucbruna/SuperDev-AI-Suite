"""Architecture score: overall platform architecture quality (0..100)."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.core.metrics_engine import graph_metrics
from modules.architecture_graph.core.topology_engine import layer_violations
from modules.architecture_graph.dependency.circular_detector import find_cycles
from modules.architecture_graph.dependency.dead_code_detector import find_dead_files
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def architecture_score(graph: ArchitectureGraph) -> dict[str, Any]:
    """Weighted composite score across modularity, layering and integrity."""
    metrics = graph_metrics(graph)
    cycles = find_cycles(graph)
    violations = layer_violations(graph)
    dead = find_dead_files(graph)
    total = max(1, metrics["nodes"])

    # Modularity: density + coupling balance (density ~0.05-0.2 is healthy).
    density = metrics.get("density", 0.0)
    if 0.01 <= density <= 0.35:
        modularity = 90.0
    elif density <= 0.5:
        modularity = 60.0
    else:
        modularity = 30.0

    # Layering: violations cost 15 points each up to a cap.
    layering = max(0.0, 100.0 - min(len(violations) * 15.0, 80.0))

    # Cycles: any cycle in file graph is penalized heavily.
    cycle_nodes = sum(c["size"] for c in cycles)
    integrity = max(0.0, 100.0 - min(cycle_nodes * 4.0, 70.0) - min(len(dead) * 0.4, 20.0))

    # Documentation: docs nodes present?
    doc_count = sum(1 for n in graph.nodes() if n.kind in {"document", "config"})
    documentation = min(100.0, doc_count * 5.0)

    total_score = round(
        0.35 * modularity + 0.30 * layering + 0.25 * integrity + 0.10 * documentation,
        1,
    )
    return {
        "score": total_score,
        "grade": _grade(total_score),
        "components": {
            "modularity": round(modularity, 1),
            "layering": round(layering, 1),
            "integrity": round(integrity, 1),
            "documentation": round(documentation, 1),
        },
        "signals": {
            "density": density,
            "layer_violations": len(violations),
            "cycles": len(cycles),
            "cycle_nodes": cycle_nodes,
            "dead_files": len(dead),
            "documents": doc_count,
        },
    }


def _grade(score: float) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"
