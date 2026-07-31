"""
Sync Engine - Core synchronization
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class SyncDirection(Enum):
    BIDIRECTIONAL = "bidirectional"
    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"


class SyncStatus(Enum):
    IDLE = "idle"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class SyncJob:
    job_id: str
    name: str
    source_id: str
    target_id: str
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    status: SyncStatus = SyncStatus.IDLE
    last_sync: Optional[datetime] = None
    records_synced: int = 0
    errors: int = 0


class SyncEngine:
    def __init__(self):
        self.jobs: Dict[str, SyncJob] = {}
        self.schedules: Dict[str, Dict[str, Any]] = {}
        self.sync_log: List[Dict[str, Any]] = []

    def create_job(self, name: str, source_id: str, target_id: str, direction: SyncDirection = SyncDirection.BIDIRECTIONAL) -> SyncJob:
        job_id = hashlib.sha256(f"{name}{source_id}{target_id}".encode()).hexdigest()[:16]
        job = SyncJob(job_id=job_id, name=name, source_id=source_id, target_id=target_id, direction=direction)
        self.jobs[job_id] = job
        return job

    def execute_sync(self, job_id: str, data: Any = None) -> Dict[str, Any]:
        job = self.jobs.get(job_id)
        if not job:
            return {"success": False, "error": "Job not found"}
        job.status = SyncStatus.SYNCING
        try:
            records = len(data) if isinstance(data, (list, dict)) else 1
            job.records_synced += records
            job.status = SyncStatus.COMPLETED
            job.last_sync = datetime.now()
            self.sync_log.append({"job_id": job_id, "records": records, "timestamp": datetime.now().isoformat(), "success": True})
            return {"success": True, "records_synced": records}
        except Exception as e:
            job.status = SyncStatus.FAILED
            job.errors += 1
            return {"success": False, "error": str(e)}

    def schedule_job(self, job_id: str, interval_seconds: int = 3600) -> None:
        self.schedules[job_id] = {"interval": interval_seconds, "last_run": None, "next_run": datetime.now().isoformat()}

    def get_job(self, job_id: str) -> Optional[SyncJob]:
        return self.jobs.get(job_id)

    def list_jobs(self) -> List[SyncJob]:
        return list(self.jobs.values())

    def get_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.sync_log[-limit:]

    def count(self) -> int:
        return len(self.jobs)
