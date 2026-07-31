"""
Audit Log
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AuditEntry:
    id: str
    action: str
    user_id: str
    resource: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    ip_address: str = ""
    success: bool = True


class AuditLog:
    def __init__(self):
        self.entries: list[AuditEntry] = []
        self.max_entries: int = 10000

    def log(self, action: str, user_id: str, resource: str = "", details: dict | None = None, success: bool = True) -> AuditEntry:
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            action=action,
            user_id=user_id,
            resource=resource,
            details=details or {},
            success=success
        )
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        return entry

    def get_by_user(self, user_id: str) -> list[AuditEntry]:
        return [e for e in self.entries if e.user_id == user_id]

    def get_by_action(self, action: str) -> list[AuditEntry]:
        return [e for e in self.entries if e.action == action]

    def get_recent(self, count: int = 100) -> list[AuditEntry]:
        return self.entries[-count:]

    def render(self) -> dict[str, Any]:
        return {"totalEntries": len(self.entries), "recent": [{"action": e.action, "userId": e.user_id} for e in self.entries[-10:]]}
