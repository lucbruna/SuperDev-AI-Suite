from typing import Any, Dict, List, Optional
from .audit_manager import AuditEntry


class AuditRepository:
    def __init__(self) -> None:
        self._store: Dict[str, AuditEntry] = {}

    def save(self, entry: AuditEntry) -> None:
        self._store[entry.id] = entry

    def get_by_id(self, id: str) -> Optional[AuditEntry]:
        return self._store.get(id)

    def get_by_actor(self, actor_id: str) -> List[AuditEntry]:
        return [e for e in self._store.values() if e.actor_id == actor_id]

    def get_by_resource(self, resource_type: str, resource_id: str) -> List[AuditEntry]:
        return [
            e
            for e in self._store.values()
            if e.resource_type == resource_type and e.resource_id == resource_id
        ]

    def list(self, limit: int = 100, offset: int = 0) -> List[AuditEntry]:
        entries = sorted(self._store.values(), key=lambda e: e.timestamp, reverse=True)
        return entries[offset : offset + limit]

    def count(self) -> int:
        return len(self._store)
