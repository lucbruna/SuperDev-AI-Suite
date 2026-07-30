from __future__ import annotations

from typing import Any

from .node import Node
from .edge import Edge


class Graph:
    """Directed Acyclic Graph for workflow dependencies."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: list[Edge] = []

    def add_node(self, node_id: str, data: dict[str, Any] | None = None) -> Node:
        node = Node(id=node_id, data=data or {})
        self._nodes[node_id] = node
        return node

    def add_edge(self, source: str, target: str) -> Edge:
        edge = Edge(source=source, target=target)
        self._edges.append(edge)
        return edge

    def get_node(self, node_id: str) -> Node | None:
        return self._nodes.get(node_id)

    def get_edges(self) -> list[Edge]:
        return list(self._edges)

    def get_children(self, node_id: str) -> list[Node]:
        children_ids = [e.target for e in self._edges if e.source == node_id]
        return [self._nodes[cid] for cid in children_ids if cid in self._nodes]

    def get_parents(self, node_id: str) -> list[Node]:
        parent_ids = [e.source for e in self._edges if e.target == node_id]
        return [self._nodes[pid] for pid in parent_ids if pid in self._nodes]

    def validate(self) -> list[str]:
        errors: list[str] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            for child in self.get_children(node_id):
                if child.id in rec_stack:
                    errors.append(f"Cycle detected at node: {child.id}")
                    return True
                if child.id not in visited:
                    if dfs(child.id):
                        return True
            rec_stack.discard(node_id)
            return False

        for node_id in self._nodes:
            if node_id not in visited:
                dfs(node_id)
        return errors

    def __len__(self) -> int:
        return len(self._nodes)
