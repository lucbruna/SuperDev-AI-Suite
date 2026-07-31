"""Tests for the memory/ subsystem (Volume 27, Fase 6)."""

from __future__ import annotations

import pytest

from enterprise_knowledge.knowledge_factory import build_engine
from enterprise_knowledge.knowledge_models import MemoryType
from enterprise_knowledge.memory.episodic_memory import EpisodicMemory
from enterprise_knowledge.memory.long_term import LongTermMemory
from enterprise_knowledge.memory.memory_engine import MemoryEngine
from enterprise_knowledge.memory.semantic_memory import SemanticMemory
from enterprise_knowledge.memory.short_term import ShortTermMemory
from enterprise_knowledge.memory.user_memory import UserMemory
from enterprise_knowledge.vector.vector_engine import VectorEngine


@pytest.fixture
def engine():
    engine = build_engine()
    vectors = VectorEngine(events=engine.events, metrics=engine.metrics,
                           config=engine.config, security=engine.security,
                           registry=engine.registry)
    engine.attach_subsystem("vector_engine", vectors)
    engine.attach_subsystem(
        "memory_engine",
        MemoryEngine(events=engine.events, metrics=engine.metrics,
                     config=engine.config, security=engine.security,
                     registry=engine.registry, vectors=vectors))
    return engine


class TestShortTermMemory:
    def test_remember_and_recall_lifo(self):
        memory = ShortTermMemory()
        memory.remember("primeira")
        memory.remember("segunda")
        contents = [rec.content for rec in memory.recall()]
        assert contents == ["segunda", "primeira"]

    def test_capacity_eviction(self):
        memory = ShortTermMemory(capacity=2)
        memory.remember("a")
        memory.remember("b")
        memory.remember("c")
        assert memory.count() == 2
        assert all(rec.content != "a" for rec in memory.recall())

    def test_recall_containing(self):
        memory = ShortTermMemory()
        memory.remember("sistema fiscal")
        memory.remember("receita de bolo")
        assert len(memory.recall_containing("fiscal")) == 1

    def test_clear(self):
        memory = ShortTermMemory()
        memory.remember("x")
        memory.clear()
        assert memory.count() == 0


class TestLongTermMemory:
    def test_remember_and_recall(self):
        memory = LongTermMemory()
        memory.remember("fato importante", importance=0.9)
        memory.remember("fato menor", importance=0.2)
        recalled = memory.recall()
        assert recalled[0].content == "fato importante"

    def test_min_importance_filter(self):
        memory = LongTermMemory()
        memory.remember("baixo", importance=0.1)
        memory.remember("alto", importance=0.8)
        assert len(memory.recall(min_importance=0.5)) == 1

    def test_recall_increments_access_count(self):
        memory = LongTermMemory()
        memory.remember("x", importance=0.5)
        first = memory.recall()[0]
        assert first.access_count == 1
        memory.recall()
        assert first.access_count == 2


class TestEpisodicMemory:
    def test_timeline_most_recent_first(self):
        memory = EpisodicMemory()
        memory.remember_event("criou contrato", actor="ana")
        memory.remember_event("assinou contrato", actor="bia")
        timeline = memory.timeline()
        assert timeline[0].content == "assinou contrato por bia"

    def test_events_by_actor(self):
        memory = EpisodicMemory()
        memory.remember_event("deploy", actor="dev")
        memory.remember_event("rollback", actor="dev")
        memory.remember_event("reunião", actor="pm")
        assert len(memory.events_by_actor("dev")) == 2

    def test_capacity(self):
        memory = EpisodicMemory(capacity=3)
        for index in range(5):
            memory.remember_event(f"evento {index}")
        assert memory.count() == 3


class TestSemanticMemory:
    def test_remember_fact_and_recall(self):
        memory = SemanticMemory()
        memory.remember_fact("PostgreSQL é o banco do ERP", subject="ERP")
        assert len(memory.recall("PostgreSQL")) == 1
        assert len(memory.facts_for("ERP")) == 1

    def test_vectors_indexed_when_available(self):
        vectors = VectorEngine()
        memory = SemanticMemory(vectors=vectors)
        memory.remember_fact("o módulo fiscal foi alterado em 2026")
        assert vectors.database.count() == 1
        assert memory.recall_similar("módulo fiscal")

    def test_recall_similar_without_vectors(self):
        assert SemanticMemory().recall_similar("pergunta") == []


class TestUserMemory:
    def test_preferences(self):
        memory = UserMemory()
        memory.set_preference("ana", "linguagem", "python")
        assert memory.get_preference("ana", "linguagem") == "python"
        assert memory.get_preference("ana", "timezone", "BRT") == "BRT"

    def test_remember_recall_per_owner(self):
        memory = UserMemory()
        memory.remember("ana", "prefere testes em pytest")
        memory.remember("bia", "usa windows")
        assert len(memory.recall("ana")) == 1
        assert memory.knows("ana") is True
        assert memory.knows("carol") is False


class TestMemoryEngine:
    def test_remember_registers_and_metrics(self, engine):
        record = engine.memory_engine.remember("lição aprendida",
                                               owner_id="dev")
        assert record.memory_id.startswith("mem-")
        assert engine.registry.list_memories() == [record.memory_id]
        assert engine.metrics.snapshot()["counters"].get(
            "ek.memories", 0) >= 1

    def test_recall_finds_stored(self, engine):
        engine.memory_engine.remember(
            "o problema de performance foi resolvido com índice SQL",
            memory_type=MemoryType.LONG_TERM)
        hits = engine.memory_engine.recall("performance")
        assert hits and "índice SQL" in hits[0].content

    def test_recall_similar_delegates(self, engine):
        engine.memory_engine.remember(
            "sistema fiscal alterado em 2026",
            memory_type=MemoryType.SEMANTIC)
        results = engine.memory_engine.recall_similar("fiscal")
        assert results

    def test_remember_event(self, engine):
        record = engine.memory_engine.remember_event("criou política",
                                                     actor="compliance")
        assert record.memory_type == MemoryType.EPISODIC
        assert engine.memory_engine.episodic.events_by_actor("compliance")

    def test_events_and_stats(self, engine):
        from enterprise_knowledge.knowledge_events import (
            EnterpriseKnowledgeEventType)
        seen = []
        engine.events.on(EnterpriseKnowledgeEventType.MEMORY_STORED,
                         lambda payload: seen.append(payload))
        engine.memory_engine.remember("memória de teste")
        assert len(seen) == 1
        stats = engine.memory_engine.stats()
        assert stats["long_term"] >= 1

    def test_forget_short_term(self, engine):
        engine.memory_engine.remember("efêmero",
                                      memory_type=MemoryType.SHORT_TERM)
        engine.memory_engine.forget_short_term()
        assert engine.memory_engine.short_term.count() == 0
