"""Tests for the knowledge memory subsystem."""

from __future__ import annotations

import pytest

from knowledge.knowledge_config import KnowledgeConfig
from knowledge.knowledge_models import MemoryRecord
from knowledge.memory import (
    EpisodicMemory,
    FileMemoryStorage,
    InMemoryMemoryStorage,
    LongTermMemory,
    MemoryCleanup,
    MemoryEngine,
    MemoryManager,
    MemoryOptimizer,
    ProceduralMemory,
    SemanticMemory,
    ShortTermMemory,
    WorkingMemory,
)


class TestInMemoryMemoryStorage:
    def test_save_get_list_delete(self) -> None:
        store = InMemoryMemoryStorage()
        record_id = store.save(MemoryRecord(content="a", memory_type="episodic"))
        assert record_id == "mem-1"
        assert store.get(record_id).content == "a"
        assert len(store.list("episodic")) == 1
        assert store.list("semantic") == []
        assert store.delete(record_id) is True
        assert store.count() == 0

    def test_get_increments_access_count(self) -> None:
        store = InMemoryMemoryStorage()
        record_id = store.save(MemoryRecord(content="x"))
        store.get(record_id)
        assert store.get(record_id).access_count == 2

    def test_limit_enforced(self) -> None:
        store = InMemoryMemoryStorage(limit=2)
        store.save(MemoryRecord(content="1"))
        store.save(MemoryRecord(content="2"))
        store.save(MemoryRecord(content="3"))
        assert store.count() == 2

    def test_serialization_roundtrip(self) -> None:
        store = InMemoryMemoryStorage()
        store.save(MemoryRecord(content="roundtrip", memory_type="semantic"))
        data = store.to_dict()
        restored = InMemoryMemoryStorage()
        restored.load_dict(data)
        assert restored.count() == 1
        assert restored.list()[0].content == "roundtrip"


class TestFileMemoryStorage:
    def test_persists_to_disk(self, tmp_path) -> None:
        path = tmp_path / "memory.json"
        store = FileMemoryStorage(path)
        store.save(MemoryRecord(content="persisted", memory_type="episodic"))
        reloaded = FileMemoryStorage(path)
        assert reloaded.count() == 1
        assert reloaded.list()[0].content == "persisted"


class TestMemoryTypes:
    def test_short_term_lru(self) -> None:
        memory = ShortTermMemory(capacity=2)
        memory.remember("k1", "v1")
        memory.remember("k2", "v2")
        memory.remember("k3", "v3")  # evicts k1
        assert memory.recall("k1") is None
        assert memory.recall("k2") == "v2"
        assert memory.size() == 2
        memory.forget("k2")
        assert memory.recall("k2") is None

    def test_working_memory_task_lifecycle(self) -> None:
        memory = WorkingMemory()
        memory.begin_task("task-1")
        memory.set("lang", "Python")
        assert memory.get("lang") == "Python"
        assert memory.current_task() == "task-1"
        snapshot = memory.end_task()
        assert snapshot == {"lang": "Python"}
        assert memory.current_task() is None

    def test_long_term_commit_recall(self) -> None:
        store = InMemoryMemoryStorage()
        memory = LongTermMemory(store)
        memory.commit("important knowledge", importance=0.9)
        memory.commit("less important", importance=0.1)
        assert memory.recall()[0].content == "important knowledge"

    def test_long_term_pin(self) -> None:
        memory = LongTermMemory(InMemoryMemoryStorage())
        memory.pin("api", "the API key format")
        assert memory.pinned()["api"] == "the API key format"
        assert memory.unpin("api") is True

    def test_episodic_experience(self) -> None:
        memory = EpisodicMemory(InMemoryMemoryStorage())
        memory.record_experience("login fails", "reset token", outcome="success")
        memory.record_experience("slow build", "incremental", outcome="failed")
        assert memory.find_solution("login") == "reset token"
        assert len(memory.experiences()) == 2
        assert len(memory.experiences(outcome="success")) == 1

    def test_semantic_facts(self) -> None:
        memory = SemanticMemory(InMemoryMemoryStorage())
        memory.store_fact("FastAPI is async", subject="framework")
        assert memory.facts("framework")[0].content == "FastAPI is async"
        assert memory.query("async") == ["FastAPI is async"]

    def test_procedural(self) -> None:
        memory = ProceduralMemory(InMemoryMemoryStorage())
        memory.store_procedure("deploy", ["build", "push", "run"])
        assert memory.get_procedure("deploy") == ["build", "push", "run"]
        assert memory.steps() == 3

    def test_memory_requires_store(self) -> None:
        with pytest.raises(RuntimeError):
            LongTermMemory().commit("x")


class TestMemoryCleanup:
    def test_prune_to_capacity(self) -> None:
        store = InMemoryMemoryStorage()
        for index in range(5):
            store.save(MemoryRecord(content=f"r{index}", importance=0.1))
        cleanup = MemoryCleanup(store)
        removed = cleanup.prune_to_capacity(2)
        assert removed == 3
        assert store.count() == 2

    def test_prune_low_importance(self) -> None:
        store = InMemoryMemoryStorage()
        store.save(MemoryRecord(content="keep", importance=0.9))
        store.save(MemoryRecord(content="drop", importance=0.1))
        cleanup = MemoryCleanup(store)
        removed = cleanup.prune_low_importance(threshold=0.5, keep=1)
        assert removed == 1
        assert store.count() == 1


class TestMemoryOptimizer:
    def test_deduplicate(self) -> None:
        store = InMemoryMemoryStorage()
        store.save(MemoryRecord(content="same"))
        store.save(MemoryRecord(content="same"))
        optimizer = MemoryOptimizer(store)
        assert optimizer.deduplicate() == 1
        assert store.count() == 1

    def test_reweight_boosts_accessed(self) -> None:
        store = InMemoryMemoryStorage()
        record_id = store.save(MemoryRecord(content="frequent", importance=0.2))
        store.get(record_id)
        store.get(record_id)
        store.get(record_id)
        optimizer = MemoryOptimizer(store)
        assert optimizer.reweight() == 1
        assert store.list()[0].importance > 0.2

    def test_top_keywords(self) -> None:
        store = InMemoryMemoryStorage()
        store.save(MemoryRecord(content="python knowledge base"))
        store.save(MemoryRecord(content="python agent"))
        optimizer = MemoryOptimizer(store)
        keywords = optimizer.top_keywords()
        assert keywords[0][0] == "python"


class TestMemoryEngine:
    def test_store_recall(self) -> None:
        engine = MemoryEngine()
        record_id = engine.store("engine memory", memory_type="episodic", importance=0.5)
        assert record_id.startswith("mem-")
        assert engine.recall("episodic")[0].content == "engine memory"

    def test_prune_and_optimize(self) -> None:
        engine = MemoryEngine()
        for index in range(5):
            engine.store(f"item {index}", importance=0.1)
        engine.optimize()
        assert engine.prune() >= 0

    def test_stats(self) -> None:
        engine = MemoryEngine()
        engine.store("x")
        stats = engine.stats()
        assert stats["records"] == 1


class TestMemoryManager:
    def test_facade_operations(self) -> None:
        manager = MemoryManager()
        manager.remember_current_task("lang", "Python")
        assert manager.context_snapshot()["short_term"] == {"lang": "Python"}
        manager.commit_long_term("long knowledge", importance=0.8)
        manager.log_experience("problem", "solution")
        manager.store_fact("fact here", subject="domain")
        manager.store_procedure("playbook", ["a", "b"])
        recall = manager.recall_all()
        assert len(recall["long_term"]) == 1
        assert len(recall["episodic"]) == 1
        assert len(recall["semantic"]) == 1
        assert len(recall["procedural"]) == 1
        status = manager.status()
        assert status["store_records"] == 4

    def test_file_backend_selection(self) -> None:
        config = KnowledgeConfig(extra={"memory_backend": "file"})
        manager = MemoryManager(config=config)
        assert isinstance(manager.store, FileMemoryStorage)
