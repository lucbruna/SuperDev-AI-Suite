"""Backup job management (Volume 37, Fase 5)."""

from __future__ import annotations

from devops_engine.devops_models import (BackupJob, BackupStatus,
                                         BackupType)
from devops_engine.devops_protocols import new_id, now


class BackupJobManager:
    """Tracks backup jobs from start through success or failure."""

    def __init__(self) -> None:
        self._jobs: dict[str, BackupJob] = {}

    def start(self, target: str,
              backup_type: BackupType = BackupType.FULL,
              encrypted: bool = True) -> BackupJob:
        job = BackupJob(
            backup_id=new_id("backup"),
            target=target,
            backup_type=backup_type,
            status=BackupStatus.RUNNING,
            encrypted=encrypted,
            started_at=now(),
            created_at=now(),
        )
        self._jobs[job.backup_id] = job
        return job

    def succeed(self, backup_id: str, size_bytes: int = 0) -> bool:
        job = self._jobs.get(backup_id)
        if job is None:
            return False
        job.status = BackupStatus.SUCCEEDED
        job.size_bytes = int(size_bytes)
        job.finished_at = now()
        return True

    def fail(self, backup_id: str) -> bool:
        job = self._jobs.get(backup_id)
        if job is None:
            return False
        job.status = BackupStatus.FAILED
        job.finished_at = now()
        return True

    def get(self, backup_id: str) -> BackupJob | None:
        return self._jobs.get(backup_id)

    def list(self) -> list[BackupJob]:
        return list(self._jobs.values())

    def count(self) -> int:
        return len(self._jobs)
