"""React Flow export: nodes/edges JSON consumed by the frontend canvas."""
from __future__ import annotations

import json
from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph

# Color per node kind for a consistent canvas.
_KIND_COLOR = {
    "file": "#64748b",
    "module": "#3b82f6",
    "package": "#8b5cf6",
    "api": "#f59e0b",
    "agent": "#10b981",
    "plugin": "#ef4444",
    "workflow": "#06b6d4",
    "service": "#ec4899",
    "database": "#14b8a6",
    "external": "#9ca3af",
    "config": "#78716c",
    "document": "#a3e635",
}


def _layout(graph: ArchitectureGraph, width: int = 1400, height: int = 900) -> dict[str, tuple[float, float]]:
    """Deterministic grid layout grouped by layer to keep the graph readable."""
    positions: dict[str, tuple[float, float]] = {}
    layer_rows: dict[str, list[str]] = {}
    for node in graph.nodes():
        layer_rows.setdefault(node.layer or "unknown", []).append(node.id)
    row = 0
    for layer, ids in layer_rows.items():
        col = 0
        for node_id in sorted(ids):
            positions[node_id] = (
                round(120 + col * (width - 240) / max(1, len(ids)), 1),
                round(80 + row * (height - 160) / max(1, len(layer_rows)), 1),
            )
            col += 1
        row += 1
    return positions


def to_reactflow(graph: ArchitectureGraph) -> dict[str, Any]:
    """Return {nodes: [...], edges: [...]} in React Flow JSON format."""
    positions = _layout(graph)
    nodes = []
    for node in graph.nodes():
        x, y = positions.get(node.id, (0.0, 0.0))
        color = _KIND_COLOR.get(node.kind, "#94a3b8")
        nodes.append(
            {
                "id": node.id,
                "position": {"x": x, "y": y},
                "data": {
                    "label": node.name,
                    "kind": node.kind,
                    "layer": node.layer,
                    "path": node.path,
                    "meta": node.meta,
                },
                "style": {
                    "border": f"1px solid {color}",
                    "borderRadius": "8px",
                    "background": f"{color}1a",
                    "color": "#e2e8f0",
                },
                "type": "default",
            }
        )
    edges = []
    for edge in graph.edges():
        edges.append(
            {
                "id": f"{edge.source}->{edge.target}:{edge.kind}",
                "source": edge.source,
                "target": edge.target,
                "label": edge.kind,
                "animated": edge.kind in {"calls", "imports"},
                "style": {"stroke": "#94a3b8"},
                "markerEnd": {"type": "arrowclosed"},
            }
        )
    return {"nodes": nodes, "edges": edges}


def to_json(graph: ArchitectureGraph) -> str:
    return json.dumps(to_reactflow(graph), ensure_ascii=False, indent=2)
