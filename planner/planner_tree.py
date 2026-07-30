from __future__ import annotations

from typing import Any


class PlannerTree:
    """Tree representation for hierarchical plans."""

    class TreeNode:
        def __init__(self, node_id: str, data: dict[str, Any] | None = None):
            self.id = node_id
            self.data = data or {}
            self.children: list[PlannerTree.TreeNode] = []
            self.parent: PlannerTree.TreeNode | None = None

    def __init__(self):
        self.root: PlannerTree.TreeNode | None = None
        self._nodes: dict[str, PlannerTree.TreeNode] = {}

    def add_node(self, node_id: str, parent_id: str | None = None, data: dict[str, Any] | None = None) -> TreeNode:
        node = self.TreeNode(node_id, data)
        self._nodes[node_id] = node
        if parent_id and parent_id in self._nodes:
            parent = self._nodes[parent_id]
            node.parent = parent
            parent.children.append(node)
        elif self.root is None:
            self.root = node
        return node

    def get_node(self, node_id: str) -> TreeNode | None:
        return self._nodes.get(node_id)

    def depth(self, node_id: str) -> int:
        node = self._nodes.get(node_id)
        if not node:
            return -1
        d = 0
        while node.parent:
            node = node.parent
            d += 1
        return d
