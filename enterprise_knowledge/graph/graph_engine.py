"""Graph engine: o núcleo do Knowledge Graph.

Constrói a rede conectada (Cliente -> Projeto -> Código -> Bug -> Correção)
com nós e relacionamentos tipados, consultas de caminho e visualização.
"""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_logger import get_logger
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_models import (AccessLevel, KnowledgeNode,
                                                   NodeType,
                                                   RelationshipRecord,
                                                   RelationshipType)
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity
from enterprise_knowledge.graph.entity_extractor import EntityExtractor
from enterprise_knowledge.graph.graph_query import GraphQuery
from enterprise_knowledge.graph.graph_visualizer import GraphVisualizer
from enterprise_knowledge.graph.node_manager import NodeManager
from enterprise_knowledge.graph.relationship_manager import RelationshipManager


class GraphEngine:
    """Orquestrador do Knowledge Graph (Fase 2 do Volume 27)."""

    def __init__(self, events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None,
                 config: EnterpriseKnowledgeConfig | None = None,
                 security: EnterpriseKnowledgeSecurity | None = None,
                 registry: EnterpriseKnowledgeRegistry | None = None,
                 nodes: NodeManager | None = None,
                 relationships: RelationshipManager | None = None) -> None:
        self._log = get_logger("graph")
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.config = config or EnterpriseKnowledgeConfig()
        self.security = security or EnterpriseKnowledgeSecurity()
        self.registry = registry
        self.nodes = nodes or NodeManager(registry=registry)
        self.relationships = relationships or RelationshipManager(
            registry=registry)
        self.extractor = EntityExtractor()
        self.query = GraphQuery(neighbors_fn=self.relationships.neighbors)
        self.visualizer = GraphVisualizer(
            node_label_fn=self._label_of,
            neighbors_fn=self.relationships.neighbors)

    def _label_of(self, node_id: str) -> str:
        node = self.nodes.get(node_id)
        return node.label if node is not None else node_id

    # -- node CRUD ----------------------------------------------------------
    def add_node(self, label: str,
                 node_type: NodeType = NodeType.CONCEPT,
                 properties: dict[str, Any] | None = None,
                 access_level: AccessLevel = AccessLevel.INTERNAL) -> KnowledgeNode:
        node = self.nodes.create(label, node_type, properties, access_level)
        self.metrics.increment("ek.nodes")
        self.events.publish(EnterpriseKnowledgeEventType.NODE_CREATED,
                            {"node_id": node.node_id, "label": label,
                             "node_type": node_type.value})
        return node

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        return self.nodes.get(node_id)

    def list_nodes(self) -> list[str]:
        return self.nodes.list()

    def all_nodes(self) -> list[KnowledgeNode]:
        return self.nodes.all()

    def find(self, label: str) -> list[KnowledgeNode]:
        return self.nodes.find_by_label(label)

    def find_type(self, node_type: NodeType) -> list[KnowledgeNode]:
        return self.nodes.find_by_type(node_type)

    def remove_node(self, node_id: str) -> bool:
        if not self.nodes.remove(node_id):
            return False
        self.events.publish(EnterpriseKnowledgeEventType.NODE_REMOVED,
                            {"node_id": node_id})
        return True

    # -- relationship CRUD --------------------------------------------------
    def connect(self, source_id: str, target_id: str,
                rel_type: RelationshipType = RelationshipType.CONNECTED_TO,
                properties: dict[str, Any] | None = None) -> RelationshipRecord | None:
        relationship = self.relationships.create(source_id, target_id,
                                                 rel_type, properties)
        if relationship is None:
            return None
        self.metrics.increment("ek.relationships")
        self.events.publish(EnterpriseKnowledgeEventType.RELATIONSHIP_CREATED,
                            {"relationship_id": relationship.relationship_id,
                             "source_id": source_id, "target_id": target_id,
                             "rel_type": rel_type.value})
        return relationship

    def get_relationship(self, relationship_id: str) -> RelationshipRecord | None:
        return self.relationships.get(relationship_id)

    def list_relationships(self) -> list[str]:
        return self.relationships.list()

    def all_relationships(self) -> list[RelationshipRecord]:
        return self.relationships.all()

    def neighbors(self, node_id: str) -> list[dict[str, Any]]:
        return self.relationships.neighbors(node_id)

    def connected(self, source_id: str, target_id: str) -> bool:
        return bool(self.relationships.between(source_id, target_id))

    def remove_relationship(self, relationship_id: str) -> bool:
        if not self.relationships.remove(relationship_id):
            return False
        self.events.publish(EnterpriseKnowledgeEventType.RELATIONSHIP_REMOVED,
                            {"relationship_id": relationship_id})
        return True

    # -- queries ------------------------------------------------------------
    def path(self, start: str, target: str) -> list[str]:
        return self.query.shortest_path(start, target)

    def reachable_from(self, start: str, limit: int = 100) -> list[str]:
        return self.query.reachable(start, limit)

    def components(self) -> list[list[str]]:
        return self.query.connected_components(self.nodes.list())

    def most_connected(self, limit: int = 5) -> list[tuple[str, int]]:
        return self.query.most_connected(self.nodes.list(), limit)

    # -- extraction ---------------------------------------------------------
    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        return self.extractor.entities(text)

    def extract_relations(self, text: str) -> list[dict[str, Any]]:
        return self.extractor.relations(text)

    # -- visualization ------------------------------------------------------
    def ascii(self, root: str, max_depth: int = 3) -> str:
        return self.visualizer.ascii_tree(root, max_depth)

    def mermaid(self) -> str:
        edges = [{"source": r.source_id, "target": r.target_id,
                  "rel_type": r.rel_type.value}
                 for r in self.all_relationships()]
        return self.visualizer.mermaid(edges)

    # -- stats --------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {"nodes": self.nodes.count(),
                "relationships": self.relationships.count(),
                "components": len(self.components())}
