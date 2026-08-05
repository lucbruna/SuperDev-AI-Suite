"""Cytoscape.js export: elements JSON for web visualisations."""
from __future__ import annotations

import json
from typing import Any

from modules.architecture_graph.exports.reactflow import _KIND_COLOR
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def to_cytoscape(graph: ArchitectureGraph) -> dict[str, Any]:
    """Return a Cytoscape.js ``elements`` payload."""
    elements: list[dict[str, Any]] = []
    for node in graph.nodes():
        elements.append(
            {
                "data": {
                    "id": node.id,
                    "label": node.name,
                    "kind": node.kind,
                    "layer": node.layer,
                    "path": node.path,
                    "color": _KIND_COLOR.get(node.kind, "#94a3b8"),
                },
                "classes": f"kind-{node.kind}",
            }
        )
    for edge in graph.edges():
        elements.append(
            {
                "data": {
                    "id": f"{edge.source}->{edge.target}:{edge.kind}",
                    "source": edge.source,
                    "target": edge.target,
                    "label": edge.kind,
                    "kind": edge.kind,
                },
                "classes": f"edge-{edge.kind}",
            }
        )
    return {"elements": elements}


def to_json(graph: ArchitectureGraph) -> str:
    return json.dumps(to_cytoscape(graph), ensure_ascii=False, indent=2)
