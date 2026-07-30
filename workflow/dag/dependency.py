from __future__ import annotations

from typing import Any

from .graph import Graph


class DependencyResolver:
    """Resolves dependencies within a DAG."""

    @staticmethod
    def get_direct_dependencies(graph: Graph, node_id: str) -> list[str]:
        return [e.source for e in graph.get_edges() if e.target == node_id]

    @staticmethod
    def get_all_dependencies(graph: Graph, node_id: str) -> set[str]:
        deps: set[str] = set()
        to_visit = [node_id]
        while to_visit:
            current = to_visit.pop()
            parents = DependencyResolver.get_direct_dependencies(graph, current)
            for p in parents:
                if p not in deps:
                    deps.add(p)
                    to_visit.append(p)
        return deps

    @staticmethod
    def get_dependents(graph: Graph, node_id: str) -> list[str]:
        return [e.target for e in graph.get_edges() if e.source == node_id]
