"""Tests for the core of the Knowledge Graph & Enterprise Memory Engine."""

from __future__ import annotations

import pytest

from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_engine import EnterpriseKnowledgeEngine
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_factory import build_engine
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_models import (AccessLevel, MemoryType,
                                                   NodeType, RelationshipType,
                                                   SearchMode)
from enterprise_knowledge.knowledge_protocols import (coerce_bool,
                                                      coerce_number, new_id,
                                                      normalize, safe_get,
                                                      tokenize, top_n)
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.knowledge_runtime import EnterpriseKnowledgeRuntime
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity


@pytest.fixture
def engine():
    return build_engine()


class TestConfig:
    def test_defaults_and_get(self):
        config = EnterpriseKnowledgeConfig()
        assert config.get("max_memory_items") == 1000
        assert config.get("missing", 42) == 42
        assert config.max_graph_nodes == 10000

    def test_merge_and_update(self):
        config = EnterpriseKnowledgeConfig(embedding_dimensions=16)
        config.update(search_default_limit=5)
        config.merge({"retention_default_days": 30})
        assert config.embedding_dimensions == 16
        assert config.search_default_limit == 5
        assert config.retention_default_days == 30

    def test_unknown_attr_raises(self):
        config = EnterpriseKnowledgeConfig()
        with pytest.raises(AttributeError):
            _ = config.nope


class TestModels:
    def test_enums(self):
        assert NodeType.PROJECT.value == "project"
        assert RelationshipType.RESOLVED_BY.value == "resolved_by"
        assert MemoryType.EPISODIC.value == "episodic"
        assert SearchMode.HYBRID.value == "hybrid"
        assert AccessLevel.RESTRICTED.value == "restricted"


class TestEvents:
    def test_on_publish_off(self):
        events = EnterpriseKnowledgeEvents()
        received = []
        listener = lambda payload: received.append(payload)
        events.on(EnterpriseKnowledgeEventType.NODE_CREATED, listener)
        events.publish(EnterpriseKnowledgeEventType.NODE_CREATED, {"n": 1})
        events.off(EnterpriseKnowledgeEventType.NODE_CREATED, listener)
        events.publish(EnterpriseKnowledgeEventType.NODE_CREATED, {"n": 2})
        assert received == [{"n": 1}]

    def test_once(self):
        events = EnterpriseKnowledgeEvents()
        count = []
        events.once(EnterpriseKnowledgeEventType.SEARCH_EXECUTED,
                    lambda p: count.append(p))
        events.publish(EnterpriseKnowledgeEventType.SEARCH_EXECUTED, {})
        events.publish(EnterpriseKnowledgeEventType.SEARCH_EXECUTED, {})
        assert len(count) == 1

    def test_listener_isolation(self):
        events = EnterpriseKnowledgeEvents()

        def boom(_payload):
            raise RuntimeError("boom")

        received = []
        events.on(EnterpriseKnowledgeEventType.MEMORY_STORED, boom)
        events.on(EnterpriseKnowledgeEventType.MEMORY_STORED,
                  lambda p: received.append(p))
        events.publish(EnterpriseKnowledgeEventType.MEMORY_STORED, {})
        assert received


class TestMetrics:
    def test_snapshot(self):
        metrics = EnterpriseKnowledgeMetrics()
        metrics.increment("ek.nodes")
        metrics.increment("ek.nodes")
        metrics.gauge("g", 3.5)
        snapshot = metrics.snapshot()
        assert snapshot["counters"]["ek.nodes"] == 2
        assert snapshot["gauges"]["g"] == 3.5

    def test_timing(self):
        metrics = EnterpriseKnowledgeMetrics()
        with metrics.timed("search"):
            pass
        snapshot = metrics.snapshot()
        avg, count = snapshot["timings"]["search"]
        assert count == 1
        assert avg >= 0


class TestSecurity:
    def test_sanitize(self):
        security = EnterpriseKnowledgeSecurity()
        assert security.sanitize("<script>alert(1)</script>ok") == "ok"
        assert not security.is_safe("<script>x</script>")
        assert security.is_safe("texto normal")

    def test_access_levels(self):
        security = EnterpriseKnowledgeSecurity()
        assert not security.can_access("employee", AccessLevel.RESTRICTED)
        assert security.can_access("admin", AccessLevel.RESTRICTED)
        assert security.can_access("employee", AccessLevel.INTERNAL)
        assert security.role_level("manager") == AccessLevel.CONFIDENTIAL

    def test_require_denies(self):
        security = EnterpriseKnowledgeSecurity()
        assert security.require("employee", AccessLevel.RESTRICTED) is False
        assert security.require("admin", AccessLevel.RESTRICTED) is True


class TestProtocols:
    def test_new_id(self):
        assert new_id("node").startswith("node-")
        assert new_id("relationship").startswith("rel-")

    def test_safe_get_dot_path(self):
        data = {"a": {"b": [10, 20]}}
        assert safe_get(data, "a.b.1") == 20
        assert safe_get(data, "a.c", "x") == "x"

    def test_coerce(self):
        assert coerce_bool("true") is True
        assert coerce_bool("no") is False
        assert coerce_number("3.7") == 3.7
        assert coerce_number("x", 1.0) == 1.0

    def test_text_helpers(self):
        assert tokenize("Venda duplicada!") == ["venda", "duplicada"]
        assert normalize("  a   b  ") == "a b"

    def test_top_n(self):
        items = [{"id": i, "score": i} for i in range(5)]
        top = top_n(items, lambda x: x["score"], limit=2)
        assert [t["score"] for t in top] == [4, 3]


class TestRegistry:
    def test_crud_and_stats(self):
        engine = build_engine()
        registry = engine.registry
        assert registry.stats()["nodes"] == 0
        node = engine.manager.create_node("João", NodeType.PERSON)
        assert node.node_id.startswith("node-")
        assert registry.get_node(node.node_id) is node
        assert registry.stats()["nodes"] == 1
        assert registry.remove_node(node.node_id) is True
        assert registry.stats()["nodes"] == 0


class TestRuntime:
    def test_start_stop_idempotent(self):
        runtime = EnterpriseKnowledgeRuntime()
        assert runtime.start() is True
        assert runtime.start() is True
        assert runtime.is_running() is True
        assert runtime.stop() is True
        assert runtime.stop() is True
        assert runtime.is_running() is False
        assert runtime.state()["running"] is False


class TestManagerAndEngine:
    def test_workflow_node_relationship_flow(self, engine):
        pessoa = engine.create_node("Cliente João", NodeType.PERSON)
        projeto = engine.create_node("Projeto ERP", NodeType.PROJECT)
        banco = engine.create_node("Banco PostgreSQL", NodeType.DATABASE)
        problema = engine.create_node("Problema de performance", NodeType.PROBLEM)
        solucao = engine.create_node("Índice SQL", NodeType.SOLUTION)

        engine.create_relationship(pessoa.node_id, projeto.node_id,
                                   RelationshipType.BELONGS_TO)
        engine.create_relationship(projeto.node_id, banco.node_id,
                                   RelationshipType.USES)
        engine.create_relationship(banco.node_id, problema.node_id,
                                   RelationshipType.HAS)
        engine.create_relationship(problema.node_id, solucao.node_id,
                                   RelationshipType.RESOLVED_BY)

        neighbors = engine.neighbors(projeto.node_id)
        labels = {n["node_id"] for n in neighbors}
        assert pessoa.node_id in labels and banco.node_id in labels
        assert engine.connected(problema.node_id, solucao.node_id)
        assert not engine.connected(solucao.node_id, problema.node_id)

    def test_relationship_requires_both_nodes(self, engine):
        projeto = engine.create_node("Projeto ERP", NodeType.PROJECT)
        rel = engine.create_relationship(projeto.node_id, "ghost",
                                         RelationshipType.USES)
        assert rel is None

    def test_node_events_and_metrics(self, engine):
        received = []
        engine.events.on(EnterpriseKnowledgeEventType.NODE_CREATED,
                         received.append)
        node = engine.create_node("Decisão técnica", NodeType.DECISION)
        assert received and received[-1]["node_id"] == node.node_id
        assert engine.metrics.snapshot()["counters"]["ek.nodes"] >= 1

    def test_document_lifecycle(self, engine):
        doc = engine.register_document("Contrato fornecedor ABC",
                                       content="prazo 24 meses",
                                       file_type="pdf",
                                       tags=["contrato"])
        assert doc.document_id.startswith("doc-")
        assert engine.get_document(doc.document_id) is doc
        assert doc.document_id in engine.list_documents()
        assert engine.remove_document(doc.document_id) is True
        assert engine.get_document(doc.document_id) is None

    def test_memory_store_recall(self, engine):
        memory = engine.store_memory(
            "Empresa utiliza PostgreSQL",
            memory_type=MemoryType.SEMANTIC,
            owner_id="planner-agent",
            metadata={"source": "wiki"},
            importance=0.9)
        assert memory.memory_id.startswith("mem-")
        recalled = engine.recall_memory(memory.memory_id)
        assert recalled.access_count == 1
        assert engine.metrics.snapshot()["counters"]["ek.memories"] >= 1

    def test_access_denied_event(self, engine):
        events = []
        engine.events.on(EnterpriseKnowledgeEventType.ACCESS_DENIED,
                         events.append)
        allowed = engine.check_access("rh_employee", "employee",
                                      AccessLevel.RESTRICTED)
        assert allowed is False
        assert events
        assert engine.check_access("admin", "admin",
                                   AccessLevel.RESTRICTED) is True

    def test_audit(self, engine):
        entry = engine.audit("admin", "document.read",
                             target="doc-1", outcome="allowed")
        assert entry.audit_id.startswith("aud-")
        assert engine.list_audit()
        assert engine.registry.stats()["audit_entries"] >= 1

    def test_factory_overrides(self):
        config = EnterpriseKnowledgeConfig(max_memory_items=5)
        custom = build_engine(config={"max_memory_items": 5})
        assert custom.config.max_memory_items == 5
        assert isinstance(custom.events, EnterpriseKnowledgeEvents)
        assert isinstance(custom.registry, EnterpriseKnowledgeRegistry)

    def test_attach_subsystem_and_backref(self, engine):
        class FakeGraphEngine:
            pass

        engine.attach_subsystem("graph_engine", FakeGraphEngine())
        assert isinstance(engine.graph_engine, FakeGraphEngine)
        assert isinstance(engine.manager.graph_engine, FakeGraphEngine)
        assert "graph_engine" in engine.stats()["subsystems"]

    def test_stats(self, engine):
        engine.create_node("x", NodeType.CONCEPT)
        stats = engine.stats()
        assert stats["registry"]["nodes"] >= 1
        assert "subsystems" in stats
        assert "runtime" in stats
