"""JSON serialization / deserialization for :class:`ArchitectureGraph`."""
from __future__ import annotations

import json
from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph

SERIALIZATION_VERSION = 1


def to_dict(graph: ArchitectureGraph) -> dict[str, Any]:
    return graph.to_dict()


def from_dict(data: dict[str, Any]) -> ArchitectureGraph:
    return ArchitectureGraph.from_dict(data)


def to_json(graph: ArchitectureGraph, *, compact: bool = False) -> str:
    if compact:
        return json.dumps(graph.to_dict(), ensure_ascii=False, separators=(",", ":"))
    return graph.to_json()


def from_json(payload: str) -> ArchitectureGraph:
    return ArchitectureGraph.from_json(payload)


def summary(graph: ArchitectureGraph) -> dict[str, Any]:
    """Lightweight summary used by list endpoints and dashboards."""
    stats = graph.stats()
    return {
        "name": stats["name"],
        "project_root": stats["project_root"],
        "built_at": stats["built_at"],
        "nodes": stats["nodes"],
        "edges": stats["edges"],
        "kinds": stats["kinds"],
        "layers": stats["layers"],
    }
