"""Tests for the backup subpackage (Volume 37, Fase 5)."""

from __future__ import annotations

import pytest

from devops_engine.backup import BackupEngine
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_models import BackupStatus, BackupType
from devops_engine.devops_protocols import now


@pytest.fixture()
def backup() -> BackupEngine:
    return BackupEngine()


class TestBackupJobManager:
    def test_start(self, backup: BackupEngine) -> None:
        job = backup.jobs.start("postgres", BackupType.FULL, encrypted=True)
        assert job.status == BackupStatus.RUNNING
        assert job.encrypted is True
        assert backup.jobs.count() == 1

    def test_succeed(self, backup: BackupEngine) -> None:
        job = backup.jobs.start("postgres")
        assert backup.jobs.succeed(job.backup_id, size_bytes=2048) is True
        assert job.status == BackupStatus.SUCCEEDED
        assert job.size_bytes == 2048

    def test_fail(self, backup: BackupEngine) -> None:
        job = backup.jobs.start("postgres")
        assert backup.jobs.fail(job.backup_id) is True
        assert job.status == BackupStatus.FAILED

    def test_succeed_missing(self, backup: BackupEngine) -> None:
        assert backup.jobs.succeed("nope") is False


class TestSnapshotManager:
    def test_create(self, backup: BackupEngine) -> None:
        snapshot = backup.snapshots.create("b1")
        assert snapshot.backup_id == "b1"
        assert backup.snapshots.count() == 1


class TestBackupScheduler:
    def test_due_logic(self, backup: BackupEngine) -> None:
        schedule = backup.schedule("postgres", interval_hours=1.0)
        assert backup.scheduler.due(schedule.schedule_id, now_ts=100.0) \
            is False
        assert backup.scheduler.due(schedule.schedule_id,
                                    now_ts=3600.0) is True

    def test_mark_run(self, backup: BackupEngine) -> None:
        schedule = backup.schedule("postgres", interval_hours=1.0)
        assert backup.scheduler.mark_run(schedule.schedule_id,
                                         now_ts=5000.0) is True
        assert backup.scheduler.due(schedule.schedule_id,
                                    now_ts=5001.0) is False


class TestRetentionPolicy:
    def test_prune_keeps_latest(self, backup: BackupEngine) -> None:
        snapshots = []
        for index in range(5):
            snapshot = backup.snapshots.create(f"b{index}")
            snapshot.created_at = float(index)
            snapshots.append(snapshot)
        removed = backup.prune(snapshots, keep=2)
        assert len(removed) == 3
        assert removed[0] is snapshots[0]

    def test_prune_nothing_when_under_keep(self, backup: BackupEngine) -> None:
        snapshots = [backup.snapshots.create("b1")]
        assert backup.prune(snapshots, keep=5) == []


class TestBackupEngine:
    def test_start_backup_event(self, backup: BackupEngine) -> None:
        events = DevopsEvents()
        backup.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.BACKUP_STARTED, seen.append)
        job = backup.start_backup("postgres")
        assert job.status == BackupStatus.RUNNING
        assert len(seen) == 1
        assert backup.metrics.count("devops.backup.jobs") == 1

    def test_succeed_backup_creates_snapshot(self, backup: BackupEngine) -> None:
        events = DevopsEvents()
        backup.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.SNAPSHOT_CREATED, seen.append)
        job = backup.start_backup("postgres")
        assert backup.succeed_backup(job.backup_id, size_bytes=100) is True
        assert job.status == BackupStatus.SUCCEEDED
        assert backup.snapshots.count() == 1
        assert len(seen) == 1

    def test_fail_backup(self, backup: BackupEngine) -> None:
        events = DevopsEvents()
        backup.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.BACKUP_FAILED, seen.append)
        job = backup.start_backup("postgres")
        assert backup.fail_backup(job.backup_id) is True
        assert job.status == BackupStatus.FAILED
        assert len(seen) == 1

    def test_schedule(self, backup: BackupEngine) -> None:
        schedule = backup.schedule("postgres", interval_hours=24.0)
        assert backup.scheduler.count() == 1

    def test_default_encrypted_from_config(self, backup: BackupEngine) -> None:
        job = backup.start_backup("postgres")
        assert job.encrypted is True

    def test_stats(self, backup: BackupEngine) -> None:
        job = backup.start_backup("postgres")
        backup.succeed_backup(job.backup_id)
        backup.schedule("postgres")
        stats = backup.stats()
        assert stats["jobs"] == 1
        assert stats["snapshots"] == 1
        assert stats["schedules"] == 1

    def test_prune_engine_default(self, backup: BackupEngine) -> None:
        for _ in range(3):
            job = backup.start_backup("postgres")
            backup.succeed_backup(job.backup_id)
        removed = backup.prune(keep=2)
        assert len(removed) == 1
