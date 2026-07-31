"""Audit engine."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AuditAction(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    CONFIG_CHANGE = "config_change"


class AuditSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.now)
    action: AuditAction = AuditAction.READ
    user_id: str = ""
    resource: str = ""
    details: str = ""
    ip_address: str = ""
    severity: AuditSeverity = AuditSeverity.LOW
    success: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditQuery:
    user_id: str | None = None
    action: AuditAction | None = None
    resource: str | None = None
    severity: AuditSeverity | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    limit: int = 100


class AuditEngine:
    def __init__(self, retention_days: int = 365):
        self._entries: list[AuditEntry] = []
        self._retention_days = retention_days
        self._max_entries: int = 100000

    def log(self, action: AuditAction, user_id: str = "", resource: str = "", details: str = "", ip_address: str = "", severity: AuditSeverity = AuditSeverity.LOW, success: bool = True, metadata: dict[str, Any] | None = None) -> AuditEntry:
        entry = AuditEntry(
            action=action,
            user_id=user_id,
            resource=resource,
            details=details,
            ip_address=ip_address,
            severity=severity,
            success=success,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]
        return entry

    def query(self, audit_query: AuditQuery) -> list[AuditEntry]:
        results = list(self._entries)
        if audit_query.user_id:
            results = [e for e in results if e.user_id == audit_query.user_id]
        if audit_query.action:
            results = [e for e in results if e.action == audit_query.action]
        if audit_query.resource:
            results = [e for e in results if e.resource == audit_query.resource]
        if audit_query.severity:
            results = [e for e in results if e.severity == audit_query.severity]
        if audit_query.start_time:
            results = [e for e in results if e.timestamp >= audit_query.start_time]
        if audit_query.end_time:
            results = [e for e in results if e.timestamp <= audit_query.end_time]
        return results[-audit_query.limit:]

    def get_entry(self, entry_id: str) -> AuditEntry | None:
        for e in self._entries:
            if e.entry_id == entry_id:
                return e
        return None

    def get_user_history(self, user_id: str, limit: int = 50) -> list[AuditEntry]:
        user_entries = [e for e in self._entries if e.user_id == user_id]
        return user_entries[-limit:]

    def get_resource_history(self, resource: str, limit: int = 50) -> list[AuditEntry]:
        resource_entries = [e for e in self._entries if e.resource == resource]
        return resource_entries[-limit:]

    def get_failed_actions(self, limit: int = 100) -> list[AuditEntry]:
        failed = [e for e in self._entries if not e.success]
        return failed[-limit:]

    def get_summary(self) -> dict[str, Any]:
        action_counts = {}
        for entry in self._entries:
            action = entry.action.value
            action_counts[action] = action_counts.get(action, 0) + 1
        return {
            "total_entries": len(self._entries),
            "action_counts": action_counts,
            "unique_users": len(set(e.user_id for e in self._entries if e.user_id)),
            "unique_resources": len(set(e.resource for e in self._entries if e.resource)),
            "failed_actions": len([e for e in self._entries if not e.success]),
        }

    def get_stats(self) -> dict:
        return {
            "total_entries": len(self._entries),
            "retention_days": self._retention_days,
            "max_entries": self._max_entries,
            **self.get_summary(),
        }
