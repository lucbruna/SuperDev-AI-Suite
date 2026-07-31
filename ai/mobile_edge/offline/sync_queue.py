"""Sync Queue - Data synchronization queue for offline-to-online."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SyncItemStatus(Enum):
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"
    FAILED = "failed"


@dataclass
class SyncItem:
    item_id: str
    table: str
    record_id: str
    operation: str = "upsert"
    data: dict[str, Any] = field(default_factory=dict)
    status: SyncItemStatus = SyncItemStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    synced_at: datetime | None = None
    attempts: int = 0
    error: str = ""


class SyncQueue:
    def __init__(self):
        self.items: list[SyncItem] = []

    def add(self, table: str, record_id: str, operation: str = "upsert", data: dict[str, Any] = None) -> SyncItem:
        item_id = hashlib.sha256(f"{table}{record_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        item = SyncItem(item_id=item_id, table=table, record_id=record_id, operation=operation, data=data or {})
        self.items.append(item)
        return item

    def get_pending(self) -> list[SyncItem]:
        return [i for i in self.items if i.status == SyncItemStatus.PENDING]

    def mark_syncing(self, item_id: str) -> bool:
        for item in self.items:
            if item.item_id == item_id:
                item.status = SyncItemStatus.SYNCING
                return True
        return False

    def mark_synced(self, item_id: str) -> bool:
        for item in self.items:
            if item.item_id == item_id:
                item.status = SyncItemStatus.SYNCED
                item.synced_at = datetime.now()
                return True
        return False

    def mark_conflict(self, item_id: str, error: str = "") -> bool:
        for item in self.items:
            if item.item_id == item_id:
                item.status = SyncItemStatus.CONFLICT
                item.error = error
                return True
        return False

    def get_by_table(self, table: str) -> list[SyncItem]:
        return [i for i in self.items if i.table == table]

    def count(self) -> int:
        return len(self.items)

    def count_pending(self) -> int:
        return len(self.get_pending())
