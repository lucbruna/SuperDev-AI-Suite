"""Manager for the Knowledge Graph & Enterprise Memory Engine.

Owns the core workflows and lets subsystem engines attach lazily.
"""

from __future__ import annotations

import time
from typing import Any

from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_context import EnterpriseKnowledgeContext
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_logger import get_logger
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_models import (AccessLevel,
                                                   AuditRecord, DocumentRecord,
                                                   IndexEntry, KnowledgeNode,
                                                   MemoryRecord, MemoryType,
                                                   NodeType,
                                                   RelationshipRecord,
                                                   RelationshipType)
from enterprise_knowledge.knowledge_protocols import new_id
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity


class EnterpriseKnowledgeManager:
    """Core orchestration: nodes, relationships, documents, memories, audit."""

    def __init__(self, registry: EnterpriseKnowledgeRegistry,
                 events: EnterpriseKnowledgeEvents,
                 metrics: EnterpriseKnowledgeMetrics,
                 config: EnterpriseKnowledgeConfig,
                 context: EnterpriseKnowledgeContext,
                 security: EnterpriseKnowledgeSecurity,
                 engine: Any = None) -> None:
        self._log = get_logger("manager")
        self.registry = registry
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.security = security
        self.engine = engine
        self._subsystems: dict[str, Any] = {}

    # -- knowledge graph ----------------------------------------------------
    def create_node(self, label: str,
                    node_type: NodeType = NodeType.CONCEPT,
                    properties: dict[str, Any] | None = None,
                    access_level: AccessLevel = AccessLevel.INTERNAL) -> KnowledgeNode:
        node = KnowledgeNode(node_id=new_id("node"), node_type=node_type,
                             label=label, properties=dict(properties or {}),
                             access_level=access_level, created_at=time.time())
        self.registry.register_node(node)
        self.metrics.increment("ek.nodes")
        self.events.publish(EnterpriseKnowledgeEventType.NODE_CREATED,
                            {"node_id": node.node_id, "label": label,
                             "node_type": node_type.value})
        return node

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        return self.registry.get_node(node_id)

    def list_nodes(self) -> list[str]:
        return self.registry.list_nodes()

    def update_node(self, node_id: str,
                    **fields: Any) -> KnowledgeNode | None:
        node = self.registry.get_node(node_id)
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
        self.events.publish(EnterpriseKnowledgeEventType.NODE_UPDATED,
                            {"node_id": node_id})
        return node

    def remove_node(self, node_id: str) -> bool:
        if not self.registry.remove_node(node_id):
            return False
        self.events.publish(EnterpriseKnowledgeEventType.NODE_REMOVED,
                            {"node_id": node_id})
        return True

    def create_relationship(self, source_id: str, target_id: str,
                            rel_type: RelationshipType = RelationshipType.CONNECTED_TO,
                            properties: dict[str, Any] | None = None) -> RelationshipRecord | None:
        if self.registry.get_node(source_id) is None or \
                self.registry.get_node(target_id) is None:
            return None
        relationship = RelationshipRecord(
            relationship_id=new_id("relationship"), source_id=source_id,
            target_id=target_id, rel_type=rel_type,
            properties=dict(properties or {}), created_at=time.time())
        self.registry.register_relationship(relationship)
        self.metrics.increment("ek.relationships")
        self.events.publish(EnterpriseKnowledgeEventType.RELATIONSHIP_CREATED,
                            {"relationship_id": relationship.relationship_id,
                             "source_id": source_id, "target_id": target_id,
                             "rel_type": rel_type.value})
        return relationship

    def get_relationship(self, relationship_id: str) -> RelationshipRecord | None:
        return self.registry.get_relationship(relationship_id)

    def list_relationships(self) -> list[str]:
        return self.registry.list_relationships()

    def remove_relationship(self, relationship_id: str) -> bool:
        if not self.registry.remove_relationship(relationship_id):
            return False
        self.events.publish(EnterpriseKnowledgeEventType.RELATIONSHIP_REMOVED,
                            {"relationship_id": relationship_id})
        return True

    def neighbors(self, node_id: str) -> list[dict[str, Any]]:
        """Returns the direct neighbors of a node (both directions)."""
        result = []
        for relationship in self.registry.relationships():
            if relationship.source_id == node_id:
                result.append({"node_id": relationship.target_id,
                               "direction": "out",
                               "rel_type": relationship.rel_type.value,
                               "relationship_id": relationship.relationship_id})
            elif relationship.target_id == node_id:
                result.append({"node_id": relationship.source_id,
                               "direction": "in",
                               "rel_type": relationship.rel_type.value,
                               "relationship_id": relationship.relationship_id})
        return result

    def connected(self, source_id: str, target_id: str) -> bool:
        return any(
            r.source_id == source_id and r.target_id == target_id
            for r in self.registry.relationships())

    # -- documents ----------------------------------------------------------
    def register_document(self, title: str, content: str = "",
                          source: str = "", file_type: str = "txt",
                          tags: list[str] | None = None,
                          access_level: AccessLevel = AccessLevel.INTERNAL) -> DocumentRecord:
        document = DocumentRecord(document_id=new_id("document"),
                                  title=title, content=content, source=source,
                                  file_type=file_type, tags=list(tags or []),
                                  access_level=access_level,
                                  created_at=time.time())
        self.registry.register_document(document)
        self.metrics.increment("ek.documents")
        return document

    def get_document(self, document_id: str) -> DocumentRecord | None:
        return self.registry.get_document(document_id)

    def list_documents(self) -> list[str]:
        return self.registry.list_documents()

    def remove_document(self, document_id: str) -> bool:
        if not self.registry.remove_document(document_id):
            return False
        self.events.publish(EnterpriseKnowledgeEventType.DOCUMENT_REMOVED,
                            {"document_id": document_id})
        return True

    # -- memory -------------------------------------------------------------
    def store_memory(self, content: str,
                     memory_type: MemoryType = MemoryType.SEMANTIC,
                     owner_id: str = "",
                     metadata: dict[str, Any] | None = None,
                     importance: float = 0.5) -> MemoryRecord:
        memory = MemoryRecord(memory_id=new_id("memory"),
                              memory_type=memory_type, content=content,
                              owner_id=owner_id,
                              metadata=dict(metadata or {}),
                              importance=max(0.0, min(1.0, importance)),
                              created_at=time.time())
        self.registry.register_memory(memory)
        self.metrics.increment("ek.memories")
        self.events.publish(EnterpriseKnowledgeEventType.MEMORY_STORED,
                            {"memory_id": memory.memory_id,
                             "memory_type": memory_type.value})
        return memory

    def get_memory(self, memory_id: str) -> MemoryRecord | None:
        return self.registry.get_memory(memory_id)

    def list_memories(self) -> list[str]:
        return self.registry.list_memories()

    def recall_memory(self, memory_id: str) -> MemoryRecord | None:
        memory = self.registry.get_memory(memory_id)
        if memory is None:
            return None
        memory.access_count += 1
        memory.last_accessed_at = time.time()
        self.events.publish(EnterpriseKnowledgeEventType.MEMORY_RECALLED,
                            {"memory_id": memory_id})
        return memory

    def remove_memory(self, memory_id: str) -> bool:
        return self.registry.remove_memory(memory_id)

    # -- index entry --------------------------------------------------------
    def index_entry(self, target_id: str,
                    terms: dict[str, int]) -> IndexEntry:
        entry = IndexEntry(index_id=new_id("index"), target_id=target_id,
                           terms=dict(terms), updated_at=time.time())
        self.registry.register_index(entry)
        self.metrics.increment("ek.index_entries")
        self.events.publish(EnterpriseKnowledgeEventType.INDEX_UPDATED,
                            {"index_id": entry.index_id,
                             "target_id": target_id})
        return entry

    # -- audit --------------------------------------------------------------
    def audit(self, actor: str, action: str, target: str = "",
              level: AccessLevel = AccessLevel.INTERNAL,
              outcome: str = "allowed") -> AuditRecord:
        entry = AuditRecord(audit_id=new_id("audit"), actor=actor,
                            action=action, target=target,
                            access_level=level, outcome=outcome,
                            created_at=time.time())
        self.registry.record_audit(entry)
        self.metrics.increment("ek.audit_entries")
        self.events.publish(EnterpriseKnowledgeEventType.GOVERNANCE_ACTION,
                            {"audit_id": entry.audit_id, "action": action,
                             "outcome": outcome})
        return entry

    def list_audit(self) -> list[AuditRecord]:
        return self.registry.list_audit()

    # -- governance ---------------------------------------------------------
    def check_access(self, actor: str, role: str,
                     level: AccessLevel) -> bool:
        if not self.security.can_access(role, level):
            self.events.publish(EnterpriseKnowledgeEventType.ACCESS_DENIED,
                                {"actor": actor, "role": role,
                                 "level": level.value})
            self.metrics.increment("ek.access_denied")
            return False
        return True

    # -- stats --------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {"registry": self.registry.stats(),
                "metrics": self.metrics.snapshot(),
                "subsystems": list(self._subsystems)}
