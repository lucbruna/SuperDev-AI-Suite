"""Relation builder — derive higher-level edges on top of a built graph.

Adds file-level ``depends_on`` edges (derived from ``imports``) and
cross-file ``references`` edges (entity names defined in more than one
file), deduplicated against edges the graph builder already produced.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.graph.edges import DEPENDS_ON, REFERENCES, make_edge


class RelationBuilder:
    """Derives dependency/reference relations from the base graph."""

    def depends_on_edges(self, graph: dict[str, Any]) -> list[dict[str, Any]]:
        """File-level depends_on edges mirroring each ``imports`` edge."""
        existing = self._edge_keys(graph)
        derived: list[dict[str, Any]] = []
        for edge in graph.get("edges", []):
            if edge.get("relation") != "imports":
                continue
            key = (edge["source"], edge["target"], DEPENDS_ON)
            if key in existing:
                continue
            existing.add(key)
            derived.append(make_edge(edge["source"], edge["target"], DEPENDS_ON, line=edge.get("line")))
        return derived

    def reference_edges(self, graph: dict[str, Any]) -> list[dict[str, Any]]:
        """File-level references edges for names defined in two or more files."""
        by_name: dict[str, set[str]] = {}
        for node in graph.get("nodes", []):
            if node.get("kind") in ("file", "import"):
                continue
            name = node.get("name", "")
            if name:
                by_name.setdefault(name, set()).add(node.get("file", ""))
        existing = self._edge_keys(graph)
        derived: list[dict[str, Any]] = []
        for name, files in by_name.items():
            if len(files) < 2:
                continue
            for source in sorted(files):
                for target in sorted(files):
                    if source >= target:
                        continue
                    for src, tgt in ((source, target), (target, source)):
                        key = (f"file:{src}", f"file:{tgt}", REFERENCES)
                        if key in existing:
                            continue
                        existing.add(key)
                        derived.append(make_edge(f"file:{src}", f"file:{tgt}", REFERENCES, weight=0.5))
        return derived

    def build(self, graph: dict[str, Any]) -> dict[str, Any]:
        """Return derived edges grouped by relation plus a stats summary."""
        edges = self.depends_on_edges(graph) + self.reference_edges(graph)
        by_relation: dict[str, list[dict[str, Any]]] = {DEPENDS_ON: [], REFERENCES: []}
        for edge in edges:
            by_relation.setdefault(edge["relation"], []).append(edge)
        return {
            "edges": edges,
            "relations": by_relation,
            "stats": {
                "depends_on": len(by_relation[DEPENDS_ON]),
                "references": len(by_relation[REFERENCES]),
            },
        }

    @staticmethod
    def _edge_keys(graph: dict[str, Any]) -> set[tuple[str, str, str]]:
        return {(e.get("source"), e.get("target"), e.get("relation")) for e in graph.get("edges", [])}
