"""Sync Engine - Core synchronization logic."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class SyncDirection(Enum):
    PUSH = "push"
    PULL = "pull"
    BIDIRECTIONAL = "bidirectional"


class SyncState(Enum):
    IDLE = "idle"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class SyncJob:
    job_id: str
    name: str
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    state: SyncState = SyncState.IDLE
    records_pushed: int = 0
    records_pulled: int = 0
    conflicts: int = 0
    last_sync: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)


class MobileSyncEngine:
    def __init__(self):
        self.jobs: Dict[str, SyncJob] = {}
        self.log: List[Dict[str, Any]] = []

    def create_job(self, name: str, direction: SyncDirection = SyncDirection.BIDIRECTIONAL) -> SyncJob:
        job_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        job = SyncJob(job_id=job_id, name=name, direction=direction)
        self.jobs[job_id] = job
        return job

    def execute(self, job_id: str, push_data: Any = None, pull_data: Any = None) -> Dict[str, Any]:
        job = self.jobs.get(job_id)
        if not job:
            return {"success": False, "error": "Job not found"}
        job.state = SyncState.SYNCING
        try:
            if push_data:
                job.records_pushed = len(push_data) if isinstance(push_data, (list, dict)) else 1
            if pull_data:
                job.records_pulled = len(pull_data) if isinstance(pull_data, (list, dict)) else 1
            job.state = SyncState.COMPLETED
            job.last_sync = datetime.now()
            self.log.append({"job_id": job_id, "timestamp": datetime.now().isoformat(), "success": True})
            return {"success": True, "pushed": job.records_pushed, "pulled": job.records_pulled}
        except Exception as e:
            job.state = SyncState.FAILED
            job.errors.append(str(e))
            return {"success": False, "error": str(e)}

    def get_job(self, job_id: str) -> Optional[SyncJob]:
        return self.jobs.get(job_id)

    def list_jobs(self) -> List[SyncJob]:
        return list(self.jobs.values())

    def count(self) -> int:
        return len(self.jobs)
