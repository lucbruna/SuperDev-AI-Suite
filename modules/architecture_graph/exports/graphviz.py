"""Graphviz DOT export for the architecture graph."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.exports.reactflow import _KIND_COLOR
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def _dot_id(node_id: str) -> str:
    """Sanitize a node id into a valid DOT identifier."""
    return '"' + node_id.replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_dot(graph: ArchitectureGraph) -> str:
    """Render the graph as Graphviz DOT source (ranked by layer)."""
    lines = [
        "digraph superdev {",
        "  rankdir=LR;",
        "  node [shape=box, style=\"rounded,filled\", fontname=\"Helvetica\", fontsize=10];",
        "  edge [color=\"#94a3b8\", arrowsize=0.7];",
    ]

    # Subgraphs per layer keep the DOT layout layered.
    layers: dict[str, list[str]] = {}
    for node in graph.nodes():
        layers.setdefault(node.layer or "unknown", []).append(node.id)
    for layer, ids in sorted(layers.items()):
        label = layer.replace('"', '\\"')
        lines.append(f"  subgraph cluster_{label.replace(' ', '_')} {{")
        lines.append(f"    label=\"{label}\";")
        lines.append("    style=dashed; color=\"#334155\";")
        for node_id in sorted(ids):
            node = graph.get_node(node_id)
            color = _KIND_COLOR.get(node.kind if node else "", "#94a3b8")
            name = (node.name if node else node_id).replace('"', '\\"')
            lines.append(f"    {_dot_id(node_id)} [label=\"{name}\", fillcolor=\"{color}22\", color=\"{color}\"];")
        lines.append("  }")

    for edge in graph.edges():
        lines.append(
            f"  {_dot_id(edge.source)} -> {_dot_id(edge.target)} "
            f"[label=\"{edge.kind}\"];"
        )
    lines.append("}")
    return "\n".join(lines) + "\n"


def to_dict(graph: ArchitectureGraph) -> dict[str, Any]:
    return {"format": "dot", "source": to_dot(graph)}
