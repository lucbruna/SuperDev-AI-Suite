"""Knowledge Graph & Enterprise Memory Engine (Volume 27).

Facade that wires core services and exposes subsystem engines lazily
(``engine.graph_engine``, ``engine.memory_engine``, ...) once attached.
"""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_context import EnterpriseKnowledgeContext
from enterprise_knowledge.knowledge_events import EnterpriseKnowledgeEvents
from enterprise_knowledge.knowledge_logger import get_logger
from enterprise_knowledge.knowledge_manager import EnterpriseKnowledgeManager
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_models import (AccessLevel, MemoryType,
                                                   NodeType,
                                                   RelationshipType)
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.knowledge_runtime import EnterpriseKnowledgeRuntime
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity


class EnterpriseKnowledgeEngine:
    """Aggregate facade over the Enterprise Knowledge subsystems."""

    def __init__(self, config: EnterpriseKnowledgeConfig | None = None,
                 events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None,
                 registry: EnterpriseKnowledgeRegistry | None = None,
                 security: EnterpriseKnowledgeSecurity | None = None,
                 context: EnterpriseKnowledgeContext | None = None,
                 runtime: EnterpriseKnowledgeRuntime | None = None) -> None:
        self._log = get_logger()
        self.config = config or EnterpriseKnowledgeConfig()
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.registry = registry or EnterpriseKnowledgeRegistry()
        self.security = security or EnterpriseKnowledgeSecurity()
        self.context = context or EnterpriseKnowledgeContext()
        self.runtime = runtime or EnterpriseKnowledgeRuntime()
        self.manager = EnterpriseKnowledgeManager(
            registry=self.registry, events=self.events, metrics=self.metrics,
            config=self.config, context=self.context, security=self.security,
            engine=self)
        self._subsystems: dict[str, Any] = {}

    # -- lifecycle ----------------------------------------------------------
    def start(self) -> bool:
        return self.runtime.start()

    def stop(self) -> bool:
        return self.runtime.stop()

    def run(self) -> bool:
        return self.start()

    # -- subsystem attachment ----------------------------------------------
    def attach_subsystem(self, name: str, engine: Any) -> None:
        self._subsystems[name] = engine
        setattr(self, name, engine)
        setattr(self.manager, name, engine)

    def __getattr__(self, name: str) -> Any:
        if name in self._subsystems:
            return self._subsystems[name]
        raise AttributeError(f"no subsystem or attribute '{name}'")

    # -- graph facade -------------------------------------------------------
    def create_node(self, label: str,
                    node_type: NodeType = NodeType.CONCEPT,
                    properties: dict[str, Any] | None = None,
                    access_level: AccessLevel = AccessLevel.INTERNAL):
        return self.manager.create_node(label, node_type, properties,
                                        access_level)

    def get_node(self, node_id: str):
        return self.manager.get_node(node_id)

    def list_nodes(self) -> list[str]:
        return self.manager.list_nodes()

    def update_node(self, node_id: str, **fields: Any):
        return self.manager.update_node(node_id, **fields)

    def remove_node(self, node_id: str) -> bool:
        return self.manager.remove_node(node_id)

    def create_relationship(self, source_id: str, target_id: str,
                            rel_type: RelationshipType = RelationshipType.CONNECTED_TO,
                            properties: dict[str, Any] | None = None):
        return self.manager.create_relationship(source_id, target_id,
                                                rel_type, properties)

    def neighbors(self, node_id: str) -> list[dict[str, Any]]:
        return self.manager.neighbors(node_id)

    def connected(self, source_id: str, target_id: str) -> bool:
        return self.manager.connected(source_id, target_id)

    # -- documents ----------------------------------------------------------
    def register_document(self, title: str, content: str = "",
                          source: str = "", file_type: str = "txt",
                          tags: list[str] | None = None,
                          access_level: AccessLevel = AccessLevel.INTERNAL):
        return self.manager.register_document(title, content, source,
                                              file_type, tags, access_level)

    def get_document(self, document_id: str):
        return self.manager.get_document(document_id)

    def list_documents(self) -> list[str]:
        return self.manager.list_documents()

    def remove_document(self, document_id: str) -> bool:
        return self.manager.remove_document(document_id)

    # -- memory -------------------------------------------------------------
    def store_memory(self, content: str,
                     memory_type: MemoryType = MemoryType.SEMANTIC,
                     owner_id: str = "",
                     metadata: dict[str, Any] | None = None,
                     importance: float = 0.5):
        return self.manager.store_memory(content, memory_type, owner_id,
                                         metadata, importance)

    def get_memory(self, memory_id: str):
        return self.manager.get_memory(memory_id)

    def list_memories(self) -> list[str]:
        return self.manager.list_memories()

    def recall_memory(self, memory_id: str):
        return self.manager.recall_memory(memory_id)

    # -- governance ---------------------------------------------------------
    def check_access(self, actor: str, role: str,
                     level: AccessLevel) -> bool:
        return self.manager.check_access(actor, role, level)

    def audit(self, actor: str, action: str, target: str = "",
              level: AccessLevel = AccessLevel.INTERNAL,
              outcome: str = "allowed"):
        return self.manager.audit(actor, action, target, level, outcome)

    def list_audit(self):
        return self.manager.list_audit()

    # -- misc ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "registry": self.registry.stats(),
            "subsystems": list(self._subsystems),
            "metrics": self.metrics.snapshot(),
            "runtime": self.runtime.state(),
        }
