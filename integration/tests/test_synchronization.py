"""Tests for the synchronization subsystem (synchronization/)."""

from __future__ import annotations

from integration.synchronization.conflict_resolver import ConflictResolver
from integration.synchronization.delta_tracker import DeltaTracker
from integration.synchronization.history import SyncHistory
from integration.synchronization.schedule import SyncScheduler
from integration.synchronization.sync_engine import SynchronizationEngine
from integration.synchronization.sync_job import SyncJob


class TestDeltaTracker:
    def test_watermark_and_changes(self) -> None:
        tracker = DeltaTracker()
        assert tracker.has_changes_since("erp", 10) is True  # no watermark yet
        tracker.set_watermark("erp", 10)
        assert tracker.has_changes_since("erp", 5) is False
        assert tracker.has_changes_since("erp", 12) is True
        assert tracker.watermark("erp") == 10

    def test_sources(self) -> None:
        tracker = DeltaTracker()
        tracker.set_watermark("a", 1)
        tracker.set_watermark("b", 2)
        assert tracker.sources() == ["a", "b"]


class TestConflictResolver:
    def test_newest(self) -> None:
        resolver = ConflictResolver("newest")
        source = {"id": 1, "value": "s", "updated_at": 200}
        target = {"id": 1, "value": "t", "updated_at": 100}
        assert resolver.resolve(source, target) == source
        assert resolver.resolve(target, source) == source

    def test_strategies(self) -> None:
        resolver = ConflictResolver()
        source = {"id": 1, "value": "s", "updated_at": 1}
        target = {"id": 1, "value": "t", "updated_at": 2}
        assert resolver.resolve(source, target, "source") == source
        assert resolver.resolve(source, target, "target") == target
        merged = resolver.resolve(source, target, "merge")
        assert merged["value"] == "s"
        assert "newest" in resolver.strategies()

    def test_invalid_strategy(self) -> None:
        try:
            ConflictResolver("bogus")
            raised = False
        except ValueError:
            raised = True
        assert raised


class TestSyncJob:
    def test_lifecycle(self) -> None:
        job = SyncJob("erp", "fin", entity="orders")
        assert job.status == "pending"
        job.start()
        assert job.status == "running"
        job.finish(5)
        assert job.status == "completed"
        assert job.records_synced == 5
        assert job.completed_at is not None
        assert job.to_dict()["direction"] == "source->target"

    def test_fail(self) -> None:
        job = SyncJob("a", "b")
        job.fail("connection refused")
        assert job.status == "failed"
        assert job.errors == ["connection refused"]


class TestSyncHistory:
    def test_record_and_count(self) -> None:
        history = SyncHistory()
        ok = SyncJob("a", "b")
        ok.finish(3)
        bad = SyncJob("a", "b")
        bad.fail("boom")
        history.record(ok)
        history.record(bad)
        assert history.count() == 2
        assert history.count("completed") == 1
        assert history.count("failed") == 1
        assert len(history.failures()) == 1
        history.clear()
        assert history.count() == 0


class TestSyncScheduler:
    def test_run_due(self) -> None:
        scheduler = SyncScheduler()
        runs: list[int] = []
        scheduler.register("j", lambda: runs.append(1), interval=-1)  # always due
        assert scheduler.run_due() == ["j"]
        assert scheduler.runs("j") == 1
        assert scheduler.next_run("j") is not None

    def test_unregister(self) -> None:
        scheduler = SyncScheduler()
        scheduler.register("j", lambda: None)
        assert scheduler.unregister("j") is True
        assert scheduler.unregister("j") is False
        assert scheduler.runs("j") == 0


class TestSynchronizationEngine:
    def test_sync_incremental(self) -> None:
        engine = SynchronizationEngine()
        records = [
            {"id": 1, "updated_at": 10},
            {"id": 2, "updated_at": 20},
        ]
        first = engine.sync("erp", "fin", records)
        assert first["status"] == "completed"
        assert first["records_synced"] == 2
        second = engine.sync("erp", "fin", records)
        assert second["records_synced"] == 0  # no changes after watermark
        assert engine.stats()["completed"] == 2
        assert engine.stats()["watermarks"] == 1

    def test_sync_skips_stale(self) -> None:
        engine = SynchronizationEngine()
        engine.sync("erp", "fin", [{"id": 1, "updated_at": 50}])
        # Older records are skipped.
        result = engine.sync("erp", "fin", [{"id": 1, "updated_at": 30}])
        assert result["records_synced"] == 0

    def test_sync_failure_on_missing_id(self) -> None:
        engine = SynchronizationEngine()
        result = engine.sync("erp", "fin", [{"no_id": True}])
        assert result["status"] == "failed"
        assert engine.stats()["failed"] == 1

    def test_schedule(self) -> None:
        engine = SynchronizationEngine()
        counter = {"n": 0}
        engine.schedule("daily", lambda: counter.__setitem__("n", counter["n"] + 1),
                        interval=-1)
        engine.scheduler.run_due()
        assert counter["n"] == 1
