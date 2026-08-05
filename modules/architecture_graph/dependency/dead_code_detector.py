"""Dead code detector: files with no dependents that are not entry points."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.config.graph_constants import ENTRYPOINTS
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def find_dead_files(
    graph: ArchitectureGraph,
    *,
    include_packages: bool = True,
) -> list[dict[str, Any]]:
    """Candidate dead files: no incoming edges, not an entrypoint.

    ``include_packages`` also reports orphaned package/module nodes.
    """
    dead: list[dict[str, Any]] = []
    for node in graph.nodes():
        if node.kind != "file":
            continue
        if node.path in ENTRYPOINTS or node.name in ENTRYPOINTS:
            continue
        incoming = graph.incoming(node.id)
        if incoming:
            continue
        # A file only reachable through its package containment is still dead.
        referenced = [
            e for e in graph.edges() if e.target == node.id and e.kind != "contains"
        ]
        if referenced:
            continue
        dead.append(
            {
                "id": node.id,
                "name": node.name,
                "path": node.path,
                "kind": node.kind,
                "layer": node.layer,
                "size": node.size,
            }
        )

    if include_packages:
        for node in graph.nodes():
            if node.kind not in {"module", "package"}:
                continue
            incoming = graph.incoming(node.id)
            outgoing = graph.outgoing(node.id)
            if not incoming and not outgoing:
                dead.append(
                    {
                        "id": node.id,
                        "name": node.name,
                        "path": node.path,
                        "kind": node.kind,
                        "layer": node.layer,
                        "size": 0,
                        "orphan_package": True,
                    }
                )
    return dead


def summary(dead: list[dict[str, Any]]) -> dict[str, Any]:
    files = [d for d in dead if not d.get("orphan_package")]
    packages = [d for d in dead if d.get("orphan_package")]
    return {"total": len(dead), "files": len(files), "packages": len(packages)}
