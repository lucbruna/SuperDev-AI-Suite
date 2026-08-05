"""Orphan detector: files not reachable from any entry point.

A file is considered orphaned when no entry point (main/app/cli modules or
package roots) can reach it through import edges. Orphans are strong
candidates for deletion or for being dead code.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.config.graph_constants import ENTRYPOINTS
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.core.navigation_engine import reachable


def find_orphans(graph: ArchitectureGraph) -> list[dict[str, Any]]:
    """Return file nodes that are not reachable from any entry point."""
    entry_ids = [
        n.id
        for n in graph.nodes()
        if n.kind == "file"
        and (n.name in ENTRYPOINTS or n.path in ENTRYPOINTS)
    ]
    if not entry_ids:
        # Fall back to files importing backend.app or modules entry modules.
        entry_ids = [
            n.id
            for n in graph.nodes()
            if n.kind == "file" and n.name in {"app.py", "main.py"}
        ]

    reachable_ids: set[str] = set()
    for entry_id in entry_ids:
        reachable_ids.update(reachable(graph, entry_id, direction="outgoing", max_depth=50))
        reachable_ids.add(entry_id)

    orphans: list[dict[str, Any]] = []
    for node in graph.nodes():
        if node.kind != "file":
            continue
        if node.id in reachable_ids:
            continue
        orphans.append(
            {
                "id": node.id,
                "name": node.name,
                "path": node.path,
                "layer": node.layer,
                "size": node.size,
            }
        )
    orphans.sort(key=lambda o: (o["layer"], o["path"]))
    return orphans


def summary(orphans: list[dict[str, Any]]) -> dict[str, Any]:
    by_layer: dict[str, int] = {}
    for orphan in orphans:
        layer = orphan.get("layer") or "unknown"
        by_layer[layer] = by_layer.get(layer, 0) + 1
    return {"total": len(orphans), "by_layer": by_layer}
