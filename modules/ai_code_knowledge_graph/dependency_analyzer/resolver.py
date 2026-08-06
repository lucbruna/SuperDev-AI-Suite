"""Dependency resolver — graph traversal over file-level dependencies.

Computes transitive dependency closures, reverse dependents / impact sets
and directed cycles over the knowledge graph's file nodes. Pure graph
traversal over the normalized node/edge dicts from the graph builder.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.relations.resolver import RelationResolver


class DependencyResolver:
    """File-level dependency traversal over a knowledge graph."""

    def __init__(self, graph: dict[str, Any], *, relation: str = "imports") -> None:
        self.graph = graph
        self.relation = relation
        self._forward, self._reverse = self._adjacency()

    def _adjacency(self) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
        """Build file→file adjacency (forward = depends-on direction)."""
        index = RelationResolver().node_index(self.graph)
        forward: dict[str, set[str]] = {}
        reverse: dict[str, set[str]] = {}
        for edge in self.graph.get("edges", []):
            if edge.get("relation") != self.relation:
                continue
            source = index.get(edge.get("source"))
            target = index.get(edge.get("target"))
            if not source or not target or source.get("kind") != "file" or target.get("kind") != "file":
                continue
            forward.setdefault(edge["source"], set()).add(edge["target"])
            reverse.setdefault(edge["target"], set()).add(edge["source"])
        return forward, reverse

    def dependencies(self, file_id: str, *, transitive: bool = True) -> list[str]:
        """Direct (or transitive) dependencies, dependency-first order.

        The start node is never reported as a dependency of itself, even when
        the graph contains a cycle that leads back to it.
        """
        visited: set[str] = set()
        order: list[str] = []

        def visit(node: str) -> None:
            for dep in sorted(self._forward.get(node, ())):
                if dep in visited:
                    continue
                visited.add(dep)
                if transitive:
                    visit(dep)
                if dep != file_id:
                    order.append(dep)

        visit(file_id)
        return order

    def dependents(self, file_id: str, *, transitive: bool = False) -> list[str]:
        """Files that (directly or transitively) depend on ``file_id``.

        The start node is excluded from its own dependent set.
        """
        visited: set[str] = set()
        order: list[str] = []

        def visit(node: str) -> None:
            for dep in sorted(self._reverse.get(node, ())):
                if dep in visited:
                    continue
                visited.add(dep)
                if transitive:
                    visit(dep)
                if dep != file_id:
                    order.append(dep)

        visit(file_id)
        return order

    def impact(self, file_id: str) -> list[str]:
        """Every file transitively affected by a change to ``file_id``."""
        return self.dependents(file_id, transitive=True)

    def find_cycles(self) -> list[list[str]]:
        """Detect directed cycles among file nodes (each cycle listed once)."""
        nodes = sorted(
            set(self._forward) | {target for deps in self._forward.values() for target in deps}
        )
        color: dict[str, int] = {}
        stack: list[str] = []
        cycles: list[list[str]] = []
        seen: set[tuple[str, ...]] = set()

        def dfs(node: str) -> None:
            color[node] = 1
            stack.append(node)
            for nxt in sorted(self._forward.get(node, ())):
                state = color.get(nxt, 0)
                if state == 1:
                    start = stack.index(nxt)
                    cycle = stack[start:]
                    key = tuple(sorted(cycle))
                    if key not in seen:
                        seen.add(key)
                        cycles.append(cycle)
                elif state == 0:
                    dfs(nxt)
            stack.pop()
            color[node] = 2

        for node in nodes:
            if color.get(node, 0) == 0:
                dfs(node)
        return cycles
