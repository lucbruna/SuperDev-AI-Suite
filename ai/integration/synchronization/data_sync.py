"""
Data Sync - Record-level synchronization
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SyncRecord:
    record_id: str
    source_id: str
    target_id: str
    data: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    synced_at: datetime | None = None
    hash_value: str = ""


class DataSync:
    def __init__(self):
        self.records: dict[str, SyncRecord] = {}
        self.conflicts: list[dict[str, Any]] = []

    def create_record(self, source_id: str, target_id: str, data: dict[str, Any]) -> SyncRecord:
        record_id = hashlib.sha256(f"{source_id}{target_id}{str(data)}".encode()).hexdigest()[:16]
        hash_val = hashlib.sha256(str(data).encode()).hexdigest()
        record = SyncRecord(
            record_id=record_id, source_id=source_id, target_id=target_id, data=data, hash_value=hash_val
        )
        self.records[record_id] = record
        return record

    def sync_record(self, record_id: str) -> bool:
        record = self.records.get(record_id)
        if record:
            record.status = "synced"
            record.synced_at = datetime.now()
            return True
        return False

    def detect_conflict(self, record_id: str, new_data: dict[str, Any]) -> bool:
        record = self.records.get(record_id)
        if record:
            new_hash = hashlib.sha256(str(new_data).encode()).hexdigest()
            if record.hash_value != new_hash:
                self.conflicts.append(
                    {
                        "record_id": record_id,
                        "old_data": record.data,
                        "new_data": new_data,
                        "detected_at": datetime.now().isoformat(),
                    }
                )
                record.status = "conflict"
                return True
        return False

    def resolve_conflict(self, record_id: str, resolution: dict[str, Any]) -> bool:
        record = self.records.get(record_id)
        if record:
            record.data = resolution
            record.hash_value = hashlib.sha256(str(resolution).encode()).hexdigest()
            record.status = "resolved"
            return True
        return False

    def get_record(self, record_id: str) -> SyncRecord | None:
        return self.records.get(record_id)

    def get_pending(self) -> list[SyncRecord]:
        return [r for r in self.records.values() if r.status == "pending"]

    def get_conflicts(self) -> list[dict[str, Any]]:
        return self.conflicts

    def count(self) -> int:
        return len(self.records)
