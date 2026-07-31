"""
Immutable Audit Logging
"""
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AuditEventType(Enum):
    ACCESS = "access"
    MODIFICATION = "modification"
    DELETION = "deletion"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION = "configuration"
    DATA_EXPORT = "data_export"
    SECURITY_EVENT = "security_event"


@dataclass
class AuditEntry:
    entry_id: str
    event_type: AuditEventType
    actor: str
    resource: str
    action: str
    result: str = "success"
    timestamp: datetime = field(default_factory=datetime.now)
    ip_address: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    previous_hash: str = ""
    entry_hash: str = ""


class AuditLogger:
    def __init__(self):
        self.entries: list[AuditEntry] = []
        self.last_hash: str = "genesis"

    def log(self, event_type: AuditEventType, actor: str, resource: str, action: str, result: str = "success", ip_address: str = "", metadata: dict[str, Any] = None) -> AuditEntry:
        entry_id = hashlib.sha256(f"{actor}{resource}{action}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        entry = AuditEntry(entry_id=entry_id, event_type=event_type, actor=actor, resource=resource, action=action, result=result, ip_address=ip_address, metadata=metadata or {}, previous_hash=self.last_hash)
        entry_data = json.dumps({"id": entry_id, "type": event_type.value, "actor": actor, "resource": resource, "prev": self.last_hash}, sort_keys=True)
        entry.entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()
        self.last_hash = entry.entry_hash
        self.entries.append(entry)
        return entry

    def verify_chain(self) -> bool:
        prev = "genesis"
        for entry in self.entries:
            if entry.previous_hash != prev:
                return False
            prev = entry.entry_hash
        return True

    def search(self, actor: str = None, event_type: AuditEventType = None, resource: str = None) -> list[AuditEntry]:
        results = self.entries
        if actor:
            results = [e for e in results if e.actor == actor]
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if resource:
            results = [e for e in results if e.resource == resource]
        return results

    def get_recent(self, limit: int = 100) -> list[AuditEntry]:
        return self.entries[-limit:]

    def get_by_actor(self, actor: str) -> list[AuditEntry]:
        return [e for e in self.entries if e.actor == actor]

    def count(self) -> int:
        return len(self.entries)
