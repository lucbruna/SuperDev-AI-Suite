"""Tests for the memory/ subpackage (Volume 31, Fase 4)."""

from __future__ import annotations

from agent_orchestration.memory import (AgentMemory, ExperienceStore,
                                        LessonManager, LongMemory, MemoryEngine,
                                        ShortMemory)
from agent_orchestration.orchestrator_events import OrchestratorEventType
from agent_orchestration.orchestrator_models import (ExecutionResult,
                                                     TaskStatus)
from agent_orchestration.orchestrator_protocols import new_id


class TestAgentMemory:
    def test_remember_recall_forget(self):
        memory = AgentMemory()
        memory.remember("a1", "lang", "python")
        assert memory.recall("a1", "lang") == "python"
        assert memory.recall("a1", "missing") is None
        assert memory.recall("a1", "missing", "x") == "x"
        assert memory.forget("a1", "lang") is True
        assert memory.forget("a1", "lang") is False

    def test_per_agent_namespacing(self):
        memory = AgentMemory()
        memory.remember("a1", "k", 1)
        memory.remember("a2", "k", 2)
        assert memory.recall("a1", "k") == 1
        assert memory.recall("a2", "k") == 2

    def test_keys_and_count(self):
        memory = AgentMemory()
        memory.remember("a1", "x", 1)
        memory.remember("a1", "y", 2)
        memory.remember("a2", "z", 3)
        assert sorted(memory.keys("a1")) == ["x", "y"]
        assert memory.count("a1") == 2
        assert memory.count() == 3


class TestShortMemory:
    def test_add_and_recent(self):
        short = ShortMemory(capacity=3)
        for i in range(5):
            short.add("a1", f"e{i}")
        recent = short.recent("a1")
        assert [entry["entry"] for entry in recent] == ["e2", "e3", "e4"]

    def test_limit(self):
        short = ShortMemory()
        for i in range(10):
            short.add("a1", f"e{i}")
        assert len(short.recent("a1", 3)) == 3

    def test_clear(self):
        short = ShortMemory()
        short.add("a1", "e")
        short.clear("a1")
        assert short.count("a1") == 0
        assert short.total() == 0


class TestLongMemory:
    def test_remember_recall_and_update(self):
        long = LongMemory()
        long.remember("a1", "db", "postgres", importance=0.9)
        assert long.recall("a1", "db") == "postgres"
        long.remember("a1", "db", "mysql", importance=0.8)
        assert long.recall("a1", "db") == "mysql"

    def test_search_ranks_by_importance(self):
        long = LongMemory()
        long.remember("a1", "framework", "django", importance=0.2)
        long.remember("a1", "web stack", "django + drf", importance=0.9)
        results = long.search("a1", "django")
        assert results[0]["importance"] == 0.9

    def test_search_no_match(self):
        long = LongMemory()
        assert long.search("a1", "nada") == []


class TestExperienceStore:
    def test_record_and_count(self):
        store = ExperienceStore()
        store.record(ExecutionResult(result_id=new_id("result"),
                                     task_id="t1", agent_id="a1"))
        store.record(ExecutionResult(result_id=new_id("result"),
                                     task_id="t2", agent_id="a2",
                                     status=TaskStatus.FAILED,
                                     error="x"))
        assert store.count() == 2
        assert store.count("a1") == 1

    def test_success_rate(self):
        store = ExperienceStore()
        store.record(ExecutionResult(result_id=new_id("r"),
                                     task_id="t1", agent_id="a1"))
        store.record(ExecutionResult(result_id=new_id("r"),
                                     task_id="t2", agent_id="a1",
                                     status=TaskStatus.FAILED))
        store.record(ExecutionResult(result_id=new_id("r"),
                                     task_id="t3", agent_id="a1"))
        assert store.success_rate("a1") == 2 / 3
        assert store.success_rate("nobody") == 0.0

    def test_average_duration(self):
        store = ExperienceStore()
        store.record(ExecutionResult(result_id=new_id("r"),
                                     task_id="t1", agent_id="a1",
                                     duration=2.0))
        store.record(ExecutionResult(result_id=new_id("r"),
                                     task_id="t2", agent_id="a1",
                                     duration=4.0))
        assert store.average_duration("a1") == 3.0


class TestLessonManager:
    def test_record_and_list(self):
        lessons = LessonManager()
        lesson = lessons.record("a1", "auth", "401", "add token")
        assert lesson.topic == "auth"
        assert lessons.count() == 1
        assert len(lessons.list("a1")) == 1
        assert lessons.list("a2") == []

    def test_mark_applied(self):
        lessons = LessonManager()
        lesson = lessons.record("a1", "t", "e", "s")
        assert lessons.mark_applied(lesson.lesson_id) is True
        assert lessons.applied_count() == 1
        assert lessons.mark_applied("nope") is False


class TestMemoryEngine:
    def test_remember_recall_and_stats(self):
        engine = MemoryEngine()
        engine.remember("a1", "lang", "python")
        assert engine.recall("a1", "lang") == "python"
        stats = engine.stats()
        assert stats["facts"] == 1

    def test_short_and_long_via_facade(self):
        engine = MemoryEngine()
        engine.short.add("a1", "recente")
        engine.remember_long("a1", "db", "postgres", importance=0.9)
        assert engine.search_long("a1", "postgres")[0]["key"] == "db"
        assert engine.recent("a1")[0]["entry"] == "recente"

    def test_experience_and_success_rate(self):
        engine = MemoryEngine()
        engine.record_experience(ExecutionResult(
            result_id=new_id("r"), task_id="t1", agent_id="a1"))
        engine.record_experience(ExecutionResult(
            result_id=new_id("r"), task_id="t2", agent_id="a1",
            status=TaskStatus.FAILED, error="x"))
        assert engine.success_rate("a1") == 0.5
        assert engine.metrics.snapshot()["counters"].get(
            "ao.experiences") == 2

    def test_lesson_publishes_event(self):
        engine = MemoryEngine()
        seen: list[str] = []
        engine.events.on(OrchestratorEventType.LESSON_LEARNED,
                         lambda payload: seen.append(payload["topic"]))
        engine.record_lesson("a1", "auth", "401", "add token")
        assert seen == ["auth"]
        assert engine.metrics.snapshot()["counters"].get("ao.lessons") == 1
