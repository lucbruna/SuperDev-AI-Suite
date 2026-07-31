"""Tests for the Knowledge & Memory Engine core: config, models, events,
metrics, registry, security, factory, runtime, manager, and engine facade.
"""

from __future__ import annotations

import pytest

from knowledge import (
    KnowledgeConfig,
    KnowledgeEngine,
    KnowledgeFactory,
    KnowledgeManager,
    KnowledgeRegistry,
    KnowledgeRuntime,
)
from knowledge.knowledge_context import KnowledgeContext, KnowledgeResult
from knowledge.knowledge_events import KnowledgeEventType, KnowledgeEvents
from knowledge.knowledge_metrics import KnowledgeMetrics
from knowledge.knowledge_models import (
    Chunk,
    DocumentRecord,
    Embedding,
    Entity,
    KnowledgeItem,
    MemoryRecord,
    Relation,
    RetrievalContext,
    SearchResult,
)
from knowledge.knowledge_security import KnowledgeSecurity


class TestKnowledgeConfig:
    def test_defaults(self) -> None:
        config = KnowledgeConfig()
        assert config.workspace_id == "default"
        assert config.embedding_dimensions == 384
        assert config.similarity_threshold == 0.5
        assert config.enable_governance is True

    def test_merge(self) -> None:
        config = KnowledgeConfig()
        config.merge({"workspace_id": "w1", "custom": "x"})
        assert config.workspace_id == "w1"
        assert config.extra["custom"] == "x"


class TestKnowledgeModels:
    def test_memory_record_to_dict(self) -> None:
        record = MemoryRecord(content="hello", memory_type="semantic", importance=0.8)
        data = record.to_dict()
        assert data["content"] == "hello"
        assert data["memory_type"] == "semantic"
        assert data["importance"] == 0.8

    def test_document_record_to_dict(self) -> None:
        document = DocumentRecord(title="Doc", content="Body")
        data = document.to_dict()
        assert data["title"] == "Doc"
        assert data["version"] == 1

    def test_entity_and_relation(self) -> None:
        entity = Entity(name="SuperDev", entity_type="project")
        relation = Relation(source="SuperDev", target="RAG", relation_type="uses")
        assert entity.to_dict()["name"] == "SuperDev"
        assert relation.to_dict()["type"] == "uses"

    def test_retrieval_context_text(self) -> None:
        context = RetrievalContext(
            query="q",
            results=[SearchResult(text="first", score=0.9), SearchResult(text="second", score=0.5)],
        )
        assert context.context_text() == "first\n\nsecond"
        assert context.context_text(limit=1) == "first"

    def test_chunk_and_embedding(self) -> None:
        chunk = Chunk(text="piece", document_id="doc-1", index=0)
        embedding = Embedding(vector=[1.0, 0.0], text="piece")
        assert chunk.document_id == "doc-1"
        assert embedding.to_dict()["vector"] == [1.0, 0.0]

    def test_knowledge_item_to_dict(self) -> None:
        item = KnowledgeItem(content="x", kind="text", source="manual")
        assert item.to_dict()["kind"] == "text"


class TestKnowledgeEvents:
    def test_publish_subscribe(self) -> None:
        events = KnowledgeEvents()
        received: list[tuple[str, dict]] = []

        def listener(event_type: str, payload: dict) -> None:
            received.append((event_type, payload))

        events.on(KnowledgeEventType.MEMORY_STORED, listener)
        events.emit(KnowledgeEventType.MEMORY_STORED, {"record_id": "mem-1"})
        assert received == [(KnowledgeEventType.MEMORY_STORED, {"record_id": "mem-1"})]

    def test_off_and_once(self) -> None:
        events = KnowledgeEvents()
        calls = {"n": 0}

        def listener(event_type: str, payload: dict) -> None:
            calls["n"] += 1

        events.once(KnowledgeEventType.ERROR, listener)
        events.emit(KnowledgeEventType.ERROR)
        events.emit(KnowledgeEventType.ERROR)
        assert calls["n"] == 1
        assert events.listener_count(KnowledgeEventType.ERROR) == 0

    def test_listener_isolation(self) -> None:
        events = KnowledgeEvents()

        def bad_listener(event_type: str, payload: dict) -> None:
            raise RuntimeError("boom")

        def good_listener(event_type: str, payload: dict) -> None:
            pass

        events.on(KnowledgeEventType.SEARCH_EXECUTED, bad_listener)
        events.on(KnowledgeEventType.SEARCH_EXECUTED, good_listener)
        events.emit(KnowledgeEventType.SEARCH_EXECUTED)  # must not raise


class TestKnowledgeMetrics:
    def test_increment_and_snapshot(self) -> None:
        metrics = KnowledgeMetrics()
        metrics.increment("memory.stored")
        metrics.increment("memory.stored", 2)
        assert metrics.get("memory.stored") == 3
        snapshot = metrics.snapshot()
        assert snapshot["counters"]["memory.stored"] == 3

    def test_timing(self) -> None:
        metrics = KnowledgeMetrics()
        with metrics.time("search"):
            pass
        assert metrics.average_timing("search") >= 0.0


class TestKnowledgeRegistry:
    def test_register_and_get(self) -> None:
        registry = KnowledgeRegistry()
        registry.register_embedding_provider("test", object())
        assert registry.get_embedding_provider("test") is not None
        registry.register_vector_backend("in-memory", object())
        assert registry.get_vector_backend("in-memory") is not None
        snapshot = registry.snapshot()
        assert snapshot["embedding_providers"] == 1
        assert snapshot["vector_backends"] == 1

    def test_factories(self) -> None:
        registry = KnowledgeRegistry()

        def factory(config: KnowledgeConfig) -> str:
            return "built"

        registry.register_factory("memory_store:in-memory", factory)
        assert registry.get_factory("memory_store:in-memory") is factory
        assert registry.get_factory("missing") is None


class TestKnowledgeSecurity:
    def test_sanitize(self) -> None:
        security = KnowledgeSecurity()
        assert security.sanitize("<script>") == "&lt;script&gt;"
        assert security.sanitize_metadata({"k": "<b>"}) == {"k": "&lt;b&gt;"}

    def test_permissions(self) -> None:
        security = KnowledgeSecurity()
        security.grant("alice", "read")
        assert security.check_permission("alice", "read") is True
        assert security.check_permission("alice", "write") is False
        assert security.check_permission("bob", "read") is False
        security.grant("bob", "*")
        assert security.check_permission("bob", "anything") is True

    def test_acl(self) -> None:
        security = KnowledgeSecurity()
        security.restrict("doc-1", ["admin"])
        assert security.can_access("admin", "doc-1") is True
        assert security.can_access("bob", "doc-1") is False

    def test_enforce(self) -> None:
        security = KnowledgeSecurity()
        with pytest.raises(PermissionError):
            security.enforce("bob", "read")


class TestKnowledgeFactory:
    def test_build_manager_wires_stores(self) -> None:
        factory = KnowledgeFactory()
        manager = factory.build_manager()
        assert manager.memory_store is not None
        assert manager.document_store is not None
        assert manager.embedding_provider is not None
        assert manager.vector_store is not None

    def test_build_with_registry_providers(self) -> None:
        registry = KnowledgeRegistry()
        factory = KnowledgeFactory(config=KnowledgeConfig(workspace_id="w9"), registry=registry)
        chunker = factory.build_chunker()
        assert chunker is not None


class TestKnowledgeRuntime:
    def test_start_stop(self) -> None:
        runtime = KnowledgeRuntime()
        assert runtime.is_running is False
        runtime.start()
        assert runtime.is_running is True
        assert runtime.manager is not None
        status = runtime.status()
        assert status["started"] is True
        runtime.stop()
        assert runtime.is_running is False

    def test_start_idempotent(self) -> None:
        runtime = KnowledgeRuntime()
        runtime.start()
        manager = runtime.manager
        runtime.start()
        assert runtime.manager is manager


class TestKnowledgeManager:
    def test_store_and_recall_memory(self) -> None:
        manager = KnowledgeFactory().build_manager()
        record_id = manager.store_memory("remember this", memory_type="semantic", importance=0.9)
        assert record_id.startswith("mem-")
        records = manager.recall_memory("semantic")
        assert [record.content for record in records] == ["remember this"]

    def test_document_crud(self) -> None:
        manager = KnowledgeFactory().build_manager()
        document = DocumentRecord(title="Notes", content="Some content")
        document_id = manager.add_document(document)
        assert document_id == "doc-1"
        document = manager.get_document(document_id)
        assert document is not None
        assert document.title == "Notes"
        assert len(manager.list_documents()) == 1

    def test_embed_and_search(self) -> None:
        manager = KnowledgeFactory().build_manager()
        manager.embed("text to embed")
        manager.index_embedding("searchable content", document_id="doc-1")
        results = manager.search("searchable content")
        assert len(results) >= 1

    def test_status(self) -> None:
        manager = KnowledgeFactory().build_manager()
        status = manager.status()
        assert status["memory_configured"] is True
        assert status["embeddings_configured"] is True
        assert "metrics" in status


class TestKnowledgeEngine:
    def test_initialize_and_shutdown(self) -> None:
        engine = KnowledgeEngine().initialize()
        assert engine.status()["started"] is True
        engine.shutdown()
        assert engine.status()["started"] is False

    def test_store_recall_search(self) -> None:
        engine = KnowledgeEngine().initialize()
        result = engine.store("engine stores this", memory_type="episodic")
        assert result.success is True
        assert result.operation == "store"
        recall = engine.recall("episodic")
        assert recall.success is True
        search = engine.search("engine")
        assert search.success is True
        engine.shutdown()

    def test_result_envelope(self) -> None:
        ok_result = KnowledgeResult.ok("op", {"x": 1})
        assert ok_result.success is True and ok_result.operation == "op"
        fail_result = KnowledgeResult.fail("op", "nope")
        assert fail_result.success is False and fail_result.error == "nope"

    def test_context_with_attributes(self) -> None:
        context = KnowledgeContext(workspace_id="w1", user="alice")
        context.with_attributes(trace_id="t-1")
        assert context.get("trace_id") == "t-1"
        assert context.to_dict()["user"] == "alice"
