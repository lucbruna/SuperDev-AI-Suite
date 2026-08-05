"""Dependency engine: turns parsed files into import/dependency edges."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.dependency.dependency_mapper import map_file_dependencies
from modules.architecture_graph.graph.edge_builder import imports
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.node_builder import external_node


class DependencyEngine:
    """Adds dependency edges to a graph from parsed file records."""

    def __init__(self, project_root: str = "", known_files: set[str] | None = None) -> None:
        self.project_root = project_root
        self.known_files: set[str] = known_files or set()

    def add_file_dependencies(
        self, graph: ArchitectureGraph, parsed: dict[str, Any], rel_path: str
    ) -> int:
        """Wire all imports of one parsed file into the graph.

        Returns the number of edges added.
        """
        rel_path = rel_path.replace("\\", "/")
        source_id = f"file:{rel_path}"
        added = 0
        if not graph.has_node(source_id):
            return added

        records = map_file_dependencies(
            parsed, rel_path=rel_path, known_files=self.known_files
        )
        for record in records:
            target = record.get("target")
            if target:
                target_id = f"file:{target}"
                if graph.add_edge(
                    imports(source_id, target_id, {"module": record.get("module", "")})
                ):
                    added += 1
            elif record.get("external"):
                top = (record.get("module") or "").split(".")[0]
                if not top:
                    continue
                external_id = f"external:{top}"
                if not graph.has_node(external_id):
                    graph.add_node(external_node(top))
                if graph.add_edge(
                    imports(source_id, external_id, {"module": record.get("module", "")})
                ):
                    added += 1
        return added

    def add_dependencies_for_batch(
        self, graph: ArchitectureGraph, parsed_files: dict[str, dict[str, Any]]
    ) -> dict[str, int]:
        """Add edges for many parsed files. Returns {rel_path: edges_added}."""
        summary: dict[str, int] = {}
        for rel_path, parsed in parsed_files.items():
            summary[rel_path] = self.add_file_dependencies(graph, parsed, rel_path)
        return summary
