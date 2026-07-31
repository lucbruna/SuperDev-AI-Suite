from __future__ import annotations

from typing import Any


class TaxonomyNode:
    """A single node in the taxonomy tree."""

    def __init__(self, name: str, parent: str | None = None, data: dict[str, Any] | None = None):
        self._name = name
        self._parent = parent
        self._children: list[TaxonomyNode] = []
        self._data = data or {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> str | None:
        return self._parent

    @property
    def children(self) -> list[TaxonomyNode]:
        return list(self._children)

    @property
    def data(self) -> dict[str, Any]:
        return dict(self._data)

    def add_child(self, child: TaxonomyNode) -> None:
        self._children.append(child)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "parent": self._parent,
            "data": dict(self._data),
            "children": [c.to_dict() for c in self._children],
        }


class Taxonomy:
    """Hierarchical classification system for organizing knowledge concepts."""

    def __init__(self, root_name: str = "root"):
        self._root = TaxonomyNode(root_name)
        self._nodes: dict[str, TaxonomyNode] = {root_name: self._root}

    @property
    def root(self) -> TaxonomyNode:
        return self._root

    @property
    def nodes(self) -> dict[str, TaxonomyNode]:
        return dict(self._nodes)

    def add_node(self, name: str, parent: str | None = None, data: dict[str, Any] | None = None) -> TaxonomyNode:
        node = TaxonomyNode(name, parent=parent, data=data)
        self._nodes[name] = node
        if parent and parent in self._nodes:
            self._nodes[parent].add_child(node)
        else:
            self._root.add_child(node)
        return node

    def get_node(self, name: str) -> TaxonomyNode | None:
        return self._nodes.get(name)

    def get_ancestors(self, name: str) -> list[str]:
        ancestors: list[str] = []
        node = self._nodes.get(name)
        while node and node.parent:
            ancestors.append(node.parent)
            node = self._nodes.get(node.parent)
        return ancestors

    def get_descendants(self, name: str) -> list[str]:
        descendants: list[str] = []
        node = self._nodes.get(name)
        if node:
            self._collect_descendants(node, descendants)
        return descendants

    def _collect_descendants(self, node: TaxonomyNode, result: list[str]) -> None:
        for child in node.children:
            result.append(child.name)
            self._collect_descendants(child, result)

    def to_dict(self) -> dict[str, Any]:
        return self._root.to_dict()

    @classmethod
    def from_dict(cls, data: dict[str, Any], root_name: str = "root") -> Taxonomy:
        taxonomy = cls(root_name=root_name)
        taxonomy.add_node(root_name)
        taxonomy._build_from_dict(data, root_name)
        return taxonomy

    def _build_from_dict(self, data: dict[str, Any], parent_name: str) -> None:
        for child_data in data.get("children", []):
            name = child_data["name"]
            self.add_node(name, parent=parent_name, data=child_data.get("data"))
            self._build_from_dict(child_data, name)

    def clear(self) -> None:
        self._nodes.clear()
        self._root = TaxonomyNode("root")
        self._nodes["root"] = self._root
