"""Static SVG export (pure Python, no external tools)."""
from __future__ import annotations

import html as html_lib
from typing import Any

from modules.architecture_graph.exports.reactflow import _KIND_COLOR, _layout
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph

_NODE_W = 120
_NODE_H = 26


def to_svg(graph: ArchitectureGraph) -> str:
    positions = _layout(graph)
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">',
        "<defs>",
        '  <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">',
        '    <path d="M0,0 L0,6 L7,3 z" fill="#94a3b8"/>',
        "  </marker>",
        "</defs>",
        '<rect width="1600" height="1000" fill="#0f172a"/>',
    ]

    # Edges first (under nodes).
    for edge in graph.edges():
        sx, sy = positions.get(edge.source, (0, 0))
        tx, ty = positions.get(edge.target, (0, 0))
        parts.append(
            f'<line x1="{sx + _NODE_W / 2:.1f}" y1="{sy + _NODE_H / 2:.1f}" '
            f'x2="{tx + _NODE_W / 2:.1f}" y2="{ty + _NODE_H / 2:.1f}" '
            'stroke="#94a3b8" stroke-width="1.2" marker-end="url(#arrow)"/>'
        )

    for node in graph.nodes():
        x, y = positions.get(node.id, (0, 0))
        color = _KIND_COLOR.get(node.kind, "#94a3b8")
        label = html_lib.escape((node.name or node.id)[:20])
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{_NODE_W}" height="{_NODE_H}" '
            f'rx="6" fill="{color}22" stroke="{color}" stroke-width="1.2"/>'
        )
        parts.append(
            f'<text x="{x + _NODE_W / 2:.1f}" y="{y + _NODE_H / 2 + 4:.1f}" '
            f'text-anchor="middle" font-family="Helvetica, Arial, sans-serif" '
            f'font-size="11" fill="#e2e8f0">{label}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def to_dict(graph: ArchitectureGraph) -> dict[str, Any]:
    return {"format": "svg", "source": to_svg(graph)}
