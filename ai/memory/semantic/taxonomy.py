from __future__ import annotations

from typing import Any, Dict, List, Optional


class TaxonomyNode:
    """A node in the taxonomy tree."""

    def __init__(self, name: str, parent: str | None = None, data: Dict[str, Any] | None = None):
        self._name = name
        self._parent = parent
        self._children: List[TaxonomyNode] = []
        self._data = data or {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> str | None:
        return self._parent

    @property
    def children(self) -> List[TaxonomyNode]:
        return list(self._children)

    def add_child(self, node: TaxonomyNode) -> None:
        self._children.append(node)


class Taxonomy:
    """Hierarchical taxonomy for classifying knowledge."""

    def __init__(self, root_name: str = "root"):
        self._root = TaxonomyNode(root_name)
        self._nodes: Dict[str, TaxonomyNode] = {root_name: self._root}

    @property
    def root(self) -> TaxonomyNode:
        return self._root

    def add_node(self, name: str, parent: str | None = None, data: Dict[str, Any] | None = None) -> TaxonomyNode:
        node = TaxonomyNode(name, parent=parent, data=data)
        self._nodes[name] = node
        if parent and parent in self._nodes:
            self._nodes[parent].add_child(node)
        else:
            self._root.add_child(node)
        return node

    def get_node(self, name: str) -> TaxonomyNode | None:
        return self._nodes.get(name)

    def get_ancestors(self, name: str) -> List[str]:
        ancestors: List[str] = []
        node = self._nodes.get(name)
        while node and node.parent:
            ancestors.append(node.parent)
            node = self._nodes.get(node.parent)
        return ancestors

    def get_descendants(self, name: str) -> List[str]:
        descendants: List[str] = []
        node = self._nodes.get(name)
        if node:
            self._collect_descendants(node, descendants)
        return descendants

    def _collect_descendants(self, node: TaxonomyNode, result: List[str]) -> None:
        for child in node.children:
            result.append(child.name)
            self._collect_descendants(child, result)

    def clear(self) -> None:
        self._nodes.clear()
        self._root = TaxonomyNode("root")
        self._nodes["root"] = self._root
