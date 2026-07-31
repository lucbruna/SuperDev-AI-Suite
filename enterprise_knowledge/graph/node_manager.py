"""Node management for the Knowledge Graph."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_models import (AccessLevel, KnowledgeNode,
                                                   NodeType)
from enterprise_knowledge.knowledge_protocols import new_id


class NodeManager:
    """CRUD over graph nodes via the shared registry."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry

    def create(self, label: str,
               node_type: NodeType = NodeType.CONCEPT,
               properties: dict[str, Any] | None = None,
               access_level: AccessLevel = AccessLevel.INTERNAL) -> KnowledgeNode:
        node = KnowledgeNode(node_id=new_id("node"), node_type=node_type,
                             label=label, properties=dict(properties or {}),
                             access_level=access_level)
        if self.registry is not None:
            self.registry.register_node(node)
        return node

    def get(self, node_id: str) -> KnowledgeNode | None:
        if self.registry is None:
            return None
        return self.registry.get_node(node_id)

    def list(self) -> list[str]:
        if self.registry is None:
            return []
        return self.registry.list_nodes()

    def all(self) -> list[KnowledgeNode]:
        if self.registry is None:
            return []
        return self.registry.nodes()

    def find_by_label(self, label: str) -> list[KnowledgeNode]:
        return [n for n in self.all()
                if n.label.lower() == label.lower()]

    def find_by_type(self, node_type: NodeType) -> list[KnowledgeNode]:
        return [n for n in self.all() if n.node_type == node_type]

    def update(self, node_id: str, **fields: Any) -> KnowledgeNode | None:
        node = self.get(node_id)
        if node is None:
            return None
        for key, value in fields.items():
            if key == "label":
                node.label = value
            elif key == "node_type":
                node.node_type = value
            elif key == "properties":
                node.properties.update(value)
            elif key == "access_level":
                node.access_level = value
        return node

    def remove(self, node_id: str) -> bool:
        if self.registry is None:
            return False
        return self.registry.remove_node(node_id)

    def count(self) -> int:
        return len(self.list())

    def degree(self, node_id: str, neighbors: list[dict[str, Any]]) -> int:
        return len(neighbors)

    def by_ids(self, node_ids: list[str]) -> list[KnowledgeNode]:
        found = []
        for node_id in node_ids:
            node = self.get(node_id)
            if node is not None:
                found.append(node)
        return found
