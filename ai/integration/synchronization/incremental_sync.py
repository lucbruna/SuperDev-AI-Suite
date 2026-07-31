"""
Incremental Sync - Delta-based synchronization
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Delta:
    delta_id: str
    entity_type: str
    operation: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    applied: bool = False


class IncrementalSync:
    def __init__(self):
        self.deltas: list[Delta] = []
        self.baselines: dict[str, str] = {}
        self.last_sync_cursor: str | None = None

    def record_delta(self, entity_type: str, operation: str, data: dict[str, Any]) -> Delta:
        delta_id = hashlib.sha256(
            f"{entity_type}{operation}{str(data)}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        delta = Delta(delta_id=delta_id, entity_type=entity_type, operation=operation, data=data)
        self.deltas.append(delta)
        return delta

    def get_pending_deltas(self, entity_type: str = None) -> list[Delta]:
        results = [d for d in self.deltas if not d.applied]
        if entity_type:
            results = [d for d in results if d.entity_type == entity_type]
        return results

    def apply_delta(self, delta_id: str) -> bool:
        for delta in self.deltas:
            if delta.delta_id == delta_id:
                delta.applied = True
                return True
        return False

    def set_baseline(self, entity_type: str, cursor: str) -> None:
        self.baselines[entity_type] = cursor

    def get_baseline(self, entity_type: str) -> str | None:
        return self.baselines.get(entity_type)

    def get_changes_since(self, entity_type: str, since: datetime) -> list[Delta]:
        return [d for d in self.deltas if d.entity_type == entity_type and d.timestamp > since]

    def count(self) -> int:
        return len(self.deltas)
