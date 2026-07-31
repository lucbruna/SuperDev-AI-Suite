"""Local Database - Offline local data storage."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class LocalRecord:
    record_id: str
    table: str
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    synced: bool = False


class LocalDatabase:
    def __init__(self):
        self.tables: dict[str, dict[str, LocalRecord]] = {}
        self.sync_queue: list[str] = []

    def insert(self, table: str, record_id: str, data: dict[str, Any]) -> LocalRecord:
        if table not in self.tables:
            self.tables[table] = {}
        record = LocalRecord(record_id=record_id, table=table, data=data)
        self.tables[table][record_id] = record
        self.sync_queue.append(f"{table}:{record_id}")
        return record

    def get(self, table: str, record_id: str) -> LocalRecord | None:
        return self.tables.get(table, {}).get(record_id)

    def update(self, table: str, record_id: str, data: dict[str, Any]) -> bool:
        record = self.tables.get(table, {}).get(record_id)
        if record:
            record.data.update(data)
            record.updated_at = datetime.now()
            self.sync_queue.append(f"{table}:{record_id}")
            return True
        return False

    def delete(self, table: str, record_id: str) -> bool:
        if table in self.tables and record_id in self.tables[table]:
            del self.tables[table][record_id]
            return True
        return False

    def query(self, table: str, filter_fn=None) -> list[LocalRecord]:
        records = list(self.tables.get(table, {}).values())
        if filter_fn:
            records = [r for r in records if filter_fn(r)]
        return records

    def count(self, table: str = None) -> int:
        if table:
            return len(self.tables.get(table, {}))
        return sum(len(t) for t in self.tables.values())

    def get_sync_queue(self) -> list[str]:
        return list(self.sync_queue)

    def clear_sync_queue(self) -> int:
        count = len(self.sync_queue)
        self.sync_queue.clear()
        return count
