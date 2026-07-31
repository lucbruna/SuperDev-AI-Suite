"""Backup engine (Volume 37, Fase 5)."""

from __future__ import annotations

from devops_engine.backup.job_manager import BackupJobManager
from devops_engine.backup.retention import RetentionPolicy
from devops_engine.backup.scheduler import BackupScheduler, ScheduledBackup
from devops_engine.backup.snapshot_manager import SnapshotManager
from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import BackupJob, BackupType, Snapshot


class BackupEngine:
    """Facade over backup jobs, snapshots, scheduling and retention."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None) -> None:
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self.jobs = BackupJobManager()
        self.snapshots = SnapshotManager()
        self.scheduler = BackupScheduler()
        self.retention = RetentionPolicy()

    def start_backup(self, target: str,
                     backup_type: BackupType = BackupType.FULL,
                     encrypted: bool | None = None) -> BackupJob:
        encrypted = bool(self.config.get("backup_encrypted", True)
                         if encrypted is None else encrypted)
        job = self.jobs.start(target, backup_type, encrypted)
        self.events.publish(DevopsEventType.BACKUP_STARTED,
                            {"backup_id": job.backup_id, "target": target})
        self.metrics.increment("devops.backup.jobs")
        return job

    def succeed_backup(self, backup_id: str,
                       size_bytes: int = 0) -> bool:
        if not self.jobs.succeed(backup_id, size_bytes):
            return False
        self.events.publish(DevopsEventType.BACKUP_SUCCEEDED,
                            {"backup_id": backup_id})
        snapshot = self.snapshots.create(backup_id)
        self.events.publish(DevopsEventType.SNAPSHOT_CREATED,
                            {"snapshot_id": snapshot.snapshot_id})
        return True

    def fail_backup(self, backup_id: str) -> bool:
        if not self.jobs.fail(backup_id):
            return False
        self.events.publish(DevopsEventType.BACKUP_FAILED,
                            {"backup_id": backup_id})
        return True

    def schedule(self, target: str,
                 interval_hours: float = 24.0) -> ScheduledBackup:
        return self.scheduler.schedule(target, interval_hours)

    def prune(self, snapshots: list[Snapshot] | None = None,
              keep: int = 30) -> list[Snapshot]:
        source = snapshots if snapshots is not None \
            else self.snapshots.list()
        return self.retention.prune(source, keep)

    def stats(self) -> dict[str, int]:
        return {
            "jobs": self.jobs.count(),
            "snapshots": self.snapshots.count(),
            "schedules": self.scheduler.count(),
        }
