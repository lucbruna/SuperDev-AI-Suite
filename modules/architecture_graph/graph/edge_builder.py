"""Factories for creating typed graph edges."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import GraphEdge


def edge(
    source: str,
    target: str,
    kind: str = "depends_on",
    meta: dict[str, Any] | None = None,
) -> GraphEdge:
    """Create an edge (endpoints are validated on insertion)."""
    return GraphEdge(source=source, target=target, kind=kind, meta=meta or {})


def contains(source: str, target: str) -> GraphEdge:
    return GraphEdge(source=source, target=target, kind="contains")


def imports(source: str, target: str, meta: dict[str, Any] | None = None) -> GraphEdge:
    return GraphEdge(source=source, target=target, kind="imports", meta=meta or {})


def calls(source: str, target: str, meta: dict[str, Any] | None = None) -> GraphEdge:
    return GraphEdge(source=source, target=target, kind="calls", meta=meta or {})


def uses(source: str, target: str, meta: dict[str, Any] | None = None) -> GraphEdge:
    return GraphEdge(source=source, target=target, kind="uses", meta=meta or {})


def depends_on(source: str, target: str, meta: dict[str, Any] | None = None) -> GraphEdge:
    return GraphEdge(source=source, target=target, kind="depends_on", meta=meta or {})


def exposes(source: str, target: str) -> GraphEdge:
    return GraphEdge(source=source, target=target, kind="exposes")


def consumes(source: str, target: str) -> GraphEdge:
    return GraphEdge(source=source, target=target, kind="consumes")


def executes(source: str, target: str) -> GraphEdge:
    return GraphEdge(source=source, target=target, kind="executes")
