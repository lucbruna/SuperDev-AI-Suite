"""Central registry for the Knowledge Graph & Enterprise Memory Engine."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_models import (AuditRecord, DocumentRecord,
                                                   GovernancePolicy,
                                                   IndexEntry, KnowledgeNode,
                                                   MemoryRecord,
                                                   RelationshipRecord)


class EnterpriseKnowledgeRegistry:
    """Public CRUD over nodes, relationships, documents, memories and audit."""

    def __init__(self) -> None:
        self._nodes: dict[str, KnowledgeNode] = {}
        self._relationships: dict[str, RelationshipRecord] = {}
        self._documents: dict[str, DocumentRecord] = {}
        self._memories: dict[str, MemoryRecord] = {}
        self._index: dict[str, IndexEntry] = {}
        self._policies: dict[str, GovernancePolicy] = {}
        self._audit: list[AuditRecord] = []
        self._max_audit = 500

    # -- nodes --------------------------------------------------------------
    def register_node(self, node: KnowledgeNode) -> None:
        self._nodes[node.node_id] = node

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        return self._nodes.get(node_id)

    def list_nodes(self) -> list[str]:
        return list(self._nodes)

    def nodes(self) -> list[KnowledgeNode]:
        return list(self._nodes.values())

    def remove_node(self, node_id: str) -> bool:
        return self._nodes.pop(node_id, None) is not None

    # -- relationships ------------------------------------------------------
    def register_relationship(self, relationship: RelationshipRecord) -> None:
        self._relationships[relationship.relationship_id] = relationship

    def get_relationship(self, relationship_id: str) -> RelationshipRecord | None:
        return self._relationships.get(relationship_id)

    def list_relationships(self) -> list[str]:
        return list(self._relationships)

    def relationships(self) -> list[RelationshipRecord]:
        return list(self._relationships.values())

    def remove_relationship(self, relationship_id: str) -> bool:
        return self._relationships.pop(relationship_id, None) is not None

    # -- documents ----------------------------------------------------------
    def register_document(self, document: DocumentRecord) -> None:
        self._documents[document.document_id] = document

    def get_document(self, document_id: str) -> DocumentRecord | None:
        return self._documents.get(document_id)

    def list_documents(self) -> list[str]:
        return list(self._documents)

    def documents(self) -> list[DocumentRecord]:
        return list(self._documents.values())

    def remove_document(self, document_id: str) -> bool:
        return self._documents.pop(document_id, None) is not None

    # -- memories -----------------------------------------------------------
    def register_memory(self, memory: MemoryRecord) -> None:
        self._memories[memory.memory_id] = memory

    def get_memory(self, memory_id: str) -> MemoryRecord | None:
        return self._memories.get(memory_id)

    def list_memories(self) -> list[str]:
        return list(self._memories)

    def memories(self) -> list[MemoryRecord]:
        return list(self._memories.values())

    def remove_memory(self, memory_id: str) -> bool:
        return self._memories.pop(memory_id, None) is not None

    # -- index --------------------------------------------------------------
    def register_index(self, entry: IndexEntry) -> None:
        self._index[entry.index_id] = entry

    def get_index(self, index_id: str) -> IndexEntry | None:
        return self._index.get(index_id)

    def list_index(self) -> list[str]:
        return list(self._index)

    def remove_index(self, index_id: str) -> bool:
        return self._index.pop(index_id, None) is not None

    # -- policies -----------------------------------------------------------
    def register_policy(self, policy: GovernancePolicy) -> None:
        self._policies[policy.policy_id] = policy

    def get_policy(self, policy_id: str) -> GovernancePolicy | None:
        return self._policies.get(policy_id)

    def list_policies(self) -> list[str]:
        return list(self._policies)

    def remove_policy(self, policy_id: str) -> bool:
        return self._policies.pop(policy_id, None) is not None

    # -- audit --------------------------------------------------------------
    def record_audit(self, entry: AuditRecord) -> None:
        self._audit.append(entry)
        if len(self._audit) > self._max_audit:
            self._audit = self._audit[-self._max_audit:]

    def list_audit(self) -> list[AuditRecord]:
        return list(self._audit)

    # -- stats --------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "nodes": len(self._nodes),
            "relationships": len(self._relationships),
            "documents": len(self._documents),
            "memories": len(self._memories),
            "index_entries": len(self._index),
            "policies": len(self._policies),
            "audit_entries": len(self._audit),
        }
