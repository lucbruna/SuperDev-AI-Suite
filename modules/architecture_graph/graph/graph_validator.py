"""Structural validation of an :class:`ArchitectureGraph`.

Checks invariants such as dangling edge endpoints, duplicate node ids,
self-loops and malformed records. Used after builds and on load to guarantee
downstream engines can rely on the graph shape.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


class GraphValidationError(ValueError):
    """Raised when the graph cannot be loaded due to structural problems."""


def validate(graph: ArchitectureGraph) -> list[dict[str, Any]]:
    """Return a list of issues (empty list == valid). Does not raise."""
    issues: list[dict[str, Any]] = []

    seen: set[str] = set()
    for node in graph.nodes():
        if node.id in seen:
            issues.append({"type": "duplicate_node", "node_id": node.id})
        seen.add(node.id)
        if not node.name:
            issues.append({"type": "empty_name", "node_id": node.id})
        if not node.id:
            issues.append({"type": "empty_id", "node_id": node.id})

    seen_edges: set[tuple[str, str, str]] = set()
    for edge in graph.edges():
        key = (edge.source, edge.target, edge.kind)
        if key in seen_edges:
            issues.append(
                {"type": "duplicate_edge", "source": edge.source, "target": edge.target}
            )
        seen_edges.add(key)
        if edge.source == edge.target:
            issues.append(
                {"type": "self_loop", "source": edge.source, "target": edge.target}
            )
        if not graph.has_node(edge.source):
            issues.append(
                {"type": "dangling_source", "source": edge.source, "target": edge.target}
            )
        if not graph.has_node(edge.target):
            issues.append(
                {"type": "dangling_target", "source": edge.source, "target": edge.target}
            )

    return issues


def assert_valid(graph: ArchitectureGraph) -> None:
    """Raise :class:`GraphValidationError` when the graph has issues."""
    issues = validate(graph)
    if issues:
        raise GraphValidationError(f"Graph validation failed: {issues[:5]}")
