"""Relation resolver — query layer over the knowledge graph topology.

Validates edge endpoints, reports dangling edges and answers dependency
questions (who imports whom, what a file depends on) without mutating the
graph. Pure queries over the normalized node/edge dicts produced by the
graph builder.
"""
from __future__ import annotations

from typing import Any


class RelationResolver:
    """Pure queries over a knowledge graph's nodes and edges."""

    @staticmethod
    def node_index(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Map node id → node for O(1) endpoint lookups."""
        return {node["id"]: node for node in graph.get("nodes", [])}

    def resolve(self, graph: dict[str, Any]) -> dict[str, Any]:
        """Validate edge endpoints; return the graph plus a dangling report."""
        index = self.node_index(graph)
        dangling: list[dict[str, Any]] = []
        for edge in graph.get("edges", []):
            missing = [edge.get(end) for end in ("source", "target") if edge.get(end) not in index]
            if missing:
                dangling.append({"edge": edge, "missing": missing})
        return {
            "graph": graph,
            "dangling_edges": dangling,
            "missing_node_ids": sorted(
                {node_id for entry in dangling for node_id in entry["missing"]}
            ),
        }

    def dependencies_of(self, graph: dict[str, Any], file_id: str, *, relation: str = "imports") -> list[str]:
        """File nodes the given file depends on via ``relation`` edges."""
        index = self.node_index(graph)
        result: set[str] = set()
        for edge in graph.get("edges", []):
            if edge.get("source") != file_id or edge.get("relation") != relation:
                continue
            target = index.get(edge.get("target"))
            if target and target.get("kind") == "file":
                result.add(target["id"])
        return sorted(result)

    def importers_of(self, graph: dict[str, Any], file_id: str, *, relation: str = "imports") -> list[str]:
        """File nodes that depend on the given file via ``relation`` edges."""
        index = self.node_index(graph)
        result: set[str] = set()
        for edge in graph.get("edges", []):
            if edge.get("target") != file_id or edge.get("relation") != relation:
                continue
            source = index.get(edge.get("source"))
            if source and source.get("kind") == "file":
                result.add(source["id"])
        return sorted(result)
