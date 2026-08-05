"""Unused plugin detector: plugin nodes no file or agent references."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def find_unused_plugins(graph: ArchitectureGraph) -> list[dict[str, Any]]:
    """Plugins with no dependents and no files using them."""
    unused: list[dict[str, Any]] = []
    for node in graph.nodes():
        if node.kind != "plugin":
            continue
        incoming = graph.incoming(node.id)
        file_edges = [
            e for e in graph.edges()
            if e.target == node.id and e.kind == "uses"
        ]
        if not incoming and not file_edges:
            unused.append(
                {
                    "id": node.id,
                    "name": node.name,
                    "path": node.path,
                    "dependents": 0,
                }
            )
    return unused


def summary(unused: list[dict[str, Any]]) -> dict[str, int]:
    return {"total": len(unused)}
