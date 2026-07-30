from __future__ import annotations

from ..forgetting_engine import ForgettingEngine
from ..expiration_policy import ExpirationPolicy
from ..decay import Decay
from ..garbage_collector import GarbageCollector
from ..cleanup_scheduler import CleanupScheduler
from ..redundancy_detector import RedundancyDetector
from ..archive_manager import ArchiveManager
from ..retention_policy import RetentionPolicy


class TestForgettingEngine:
    def setup_method(self) -> None:
        self.engine = ForgettingEngine()

    def test_run_forgetting_cycle(self) -> None:
        entries = {"a": {"type": "text", "content": "x"}, "b": {"type": "text", "content": "y"}}
        result = self.engine.run_forgetting_cycle(entries)
        assert "removed_count" in result
        assert "kept_count" in result

    def test_snapshot(self) -> None:
        snap = self.engine.snapshot()
        assert "forgetting_cycles" in snap

    def test_properties(self) -> None:
        assert isinstance(self.engine.expiration, ExpirationPolicy)
        assert isinstance(self.engine.decay, Decay)
        assert isinstance(self.engine.gc, GarbageCollector)
        assert isinstance(self.engine.scheduler, CleanupScheduler)
        assert isinstance(self.engine.redundancy, RedundancyDetector)
        assert isinstance(self.engine.archive, ArchiveManager)
        assert isinstance(self.engine.retention, RetentionPolicy)


class TestExpirationPolicy:
    def setup_method(self) -> None:
        self.policy = ExpirationPolicy()

    def test_set_and_get_ttl(self) -> None:
        self.policy.set_ttl("k1", 60.0)
        assert self.policy.get_ttl("k1") == 60.0
        assert self.policy.get_ttl("nonexistent") is None

    def test_remove_ttl(self) -> None:
        self.policy.set_ttl("k", 10.0)
        assert self.policy.remove_ttl("k") is True
        assert self.policy.remove_ttl("k") is False

    def test_is_expired(self) -> None:
        import time

        self.policy.set_ttl("k", 0.0)
        assert self.policy.is_expired("k", {}) is True

    def test_expired_count(self) -> None:
        import time

        self.policy.set_ttl("a", 0.0)
        now = time.time()
        self.policy.set_ttl("b", 99999.0)
        entries = {"a": {"created_at": 0}, "b": {"created_at": now}}
        assert self.policy.expired_count(entries) == 1

    def test_clear(self) -> None:
        self.policy.set_ttl("k", 10.0)
        self.policy.clear()
        assert self.policy.get_ttl("k") is None


class TestDecay:
    def setup_method(self) -> None:
        self.decay = Decay(base_decay_rate=0.5)

    def test_record_access(self) -> None:
        self.decay.record_access("k")
        assert self.decay.last_access("k") is not None

    def test_decay_score_recent(self) -> None:
        self.decay.record_access("k")
        score = self.decay.decay_score("k", {"created_at": 0})
        assert score > 0.5

    def test_apply_decay(self) -> None:
        entries = {"old": {"created_at": 0}, "new": {"created_at": 9999999999}}
        self.decay.record_access("old")
        self.decay.record_access("new")
        result = self.decay.apply_decay(entries, threshold=0.1)
        assert isinstance(result, dict)

    def test_refresh(self) -> None:
        self.decay.refresh("k")
        assert self.decay.last_access("k") is not None

    def test_clear(self) -> None:
        self.decay.record_access("k")
        self.decay.clear()
        assert self.decay.last_access("k") is None


class TestGarbageCollector:
    def setup_method(self) -> None:
        self.gc = GarbageCollector()

    def test_collect(self) -> None:
        entries = {"a": {"active": True}, "b": {"active": False}, "c": {"active": True}}
        kept = self.gc.collect(entries)
        assert "b" not in kept
        assert self.gc.collected_count == 1

    def test_collect_empty(self) -> None:
        entries = {"a": {}, "b": {}, "c": {}}
        kept = self.gc.collect_empty(entries)
        assert len(kept) == 0

    def test_stats(self) -> None:
        entries = {"a": {"active": False}}
        self.gc.collect(entries)
        s = self.gc.stats()
        assert s["collected_count"] == 1

    def test_clear(self) -> None:
        entries = {"a": {"active": False}}
        self.gc.collect(entries)
        self.gc.clear()
        assert self.gc.collected_count == 0


class TestCleanupScheduler:
    def setup_method(self) -> None:
        self.scheduler = CleanupScheduler()

    def test_schedule_and_run(self) -> None:
        calls = []
        self.scheduler.schedule("t1", 0.0, lambda: calls.append(1))
        count = self.scheduler.run_due()
        assert count == 1

    def test_unschedule(self) -> None:
        self.scheduler.schedule("t", 1.0, lambda: None)
        assert self.scheduler.unschedule("t") is True
        assert self.scheduler.unschedule("t") is False

    def test_run_all(self) -> None:
        calls = []
        self.scheduler.schedule("a", 1.0, lambda: calls.append(1))
        self.scheduler.schedule("b", 1.0, lambda: calls.append(2))
        count = self.scheduler.run_all()
        assert count == 2

    def test_list_tasks(self) -> None:
        self.scheduler.schedule("a", 1.0, lambda: None)
        assert "a" in self.scheduler.list_tasks()

    def test_clear(self) -> None:
        self.scheduler.schedule("a", 1.0, lambda: None)
        self.scheduler.clear()
        assert self.scheduler.task_count == 0


class TestRedundancyDetector:
    def setup_method(self) -> None:
        self.detector = RedundancyDetector()

    def test_find_redundant(self) -> None:
        entries = {"a": {"x": 1, "y": 2}, "b": {"x": 1, "y": 2}, "c": {"z": 3}}
        redundant = self.detector.find_redundant(entries)
        assert len(redundant) >= 1

    def test_similarity_matrix(self) -> None:
        entries = {"a": {"x": 1}, "b": {"x": 1, "y": 2}}
        matrix = self.detector.similarity_matrix(entries)
        assert "a" in matrix
        assert "b" in matrix

    def test_clear(self) -> None:
        self.detector.find_redundant({"a": {"x": 1}, "b": {"x": 1}})
        self.detector.clear()
        assert self.detector.redundant_count == 0


class TestArchiveManager:
    def setup_method(self) -> None:
        self.manager = ArchiveManager()

    def test_archive_and_retrieve(self) -> None:
        self.manager.archive("k", "value")
        assert self.manager.retrieve("k") == "value"
        assert self.manager.retrieve("nonexistent") is None

    def test_archive_batch(self) -> None:
        count = self.manager.archive_batch({"a": 1, "b": 2})
        assert count == 2
        assert self.manager.archived_count == 2

    def test_list_archived_keys(self) -> None:
        self.manager.archive("a", 1)
        self.manager.archive("b", 2)
        assert set(self.manager.list_archived_keys()) == {"a", "b"}

    def test_search_archive(self) -> None:
        self.manager.archive("k", "hello world")
        results = self.manager.search_archive("hello")
        assert len(results) == 1

    def test_remove_archived(self) -> None:
        self.manager.archive("k", "v")
        assert self.manager.remove_archived("k") is True
        assert self.manager.remove_archived("k") is False

    def test_clear(self) -> None:
        self.manager.archive("k", "v")
        self.manager.clear()
        assert self.manager.archived_count == 0


class TestRetentionPolicy:
    def setup_method(self) -> None:
        self.policy = RetentionPolicy()

    def test_set_max_entries(self) -> None:
        self.policy.set_max_entries("text", 2)
        entries = {
            "a": {"type": "text", "created_at": 1},
            "b": {"type": "text", "created_at": 2},
            "c": {"type": "text", "created_at": 3},
        }
        kept = self.policy.enforce(entries)
        assert len(kept) <= 2

    def test_set_max_age(self) -> None:
        import time

        self.policy.set_max_age("text", 1)
        entries = {
            "old": {"type": "text", "created_at": 0},
            "new": {"type": "text", "created_at": time.time()},
        }
        kept = self.policy.enforce(entries)
        assert "old" not in kept

    def test_clear(self) -> None:
        self.policy.set_max_entries("text", 5)
        self.policy.clear()
        assert self.policy.get_max_entries("text") is None
