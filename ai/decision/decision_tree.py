from __future__ import annotations

from typing import Any


class DecisionNode:
    """A node in a decision tree."""

    def __init__(self, name: str, value: Any = None):
        self.name = name
        self.value = value
        self.children: list[DecisionNode] = []
        self.parent: DecisionNode | None = None

    def add_child(self, node: DecisionNode) -> None:
        node.parent = self
        self.children.append(node)


class DecisionTree:
    """Decision tree structure for hierarchical decisions."""

    def __init__(self, root: DecisionNode | None = None):
        self._root = root or DecisionNode("root")

    def evaluate(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        path: list[dict[str, Any]] = []
        current = self._root
        while current and current.children:
            matched = False
            for child in current.children:
                if child.name in data:
                    path.append({"node": current.name, "child": child.name, "value": data[child.name]})
                    current = child
                    matched = True
                    break
            if not matched:
                break
        return path

    def depth(self) -> int:
        def _depth(node: DecisionNode) -> int:
            if not node.children:
                return 1
            return 1 + max(_depth(c) for c in node.children)

        return _depth(self._root)
