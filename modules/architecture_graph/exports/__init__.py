"""Exporters: transform the architecture graph into external formats.

Supported formats:
* ``reactflow`` — React Flow JSON (nodes/edges) for the frontend canvas.
* ``cytoscape`` — Cytoscape.js elements JSON.
* ``graphviz`` — DOT source (rendered externally with ``dot`` if available).
* ``mermaid`` — Mermaid flowchart source.
* ``html`` — self-contained interactive HTML (vanilla JS, no deps).
* ``svg`` — static SVG rendering (pure Python).
* ``png`` / ``pdf`` — rendered via Graphviz ``dot`` when available.

All exporters are pure stdlib; PNG/PDF gracefully degrade to SVG when the
``dot`` binary is not installed.
"""
from __future__ import annotations

from modules.architecture_graph.exports import (
    cytoscape,
    graphviz,
    html,
    mermaid,
    png,
    reactflow,
    svg,
)

__all__ = [
    "cytoscape",
    "graphviz",
    "html",
    "mermaid",
    "png",
    "reactflow",
    "svg",
]
