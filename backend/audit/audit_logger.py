from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from backend.utils.uuid_utils import generate_uuid


class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_CHANGE = "permission_change"
    ROLE_CHANGE = "role_change"
    API_KEY_CREATE = "api_key_create"
    API_KEY_REVOKE = "api_key_revoke"
    PLUGIN_INSTALL = "plugin_install"
    PLUGIN_UNINSTALL = "plugin_uninstall"
    WORKFLOW_EXECUTE = "workflow_execute"
    AGENT_EXECUTE = "agent_execute"
    RUNTIME_EXECUTE = "runtime_execute"
    DEPLOY = "deploy"
    SETTINGS_CHANGE = "settings_change"
    EXPORT = "export"
    IMPORT = "import"


class AuditSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    id: str
    timestamp: datetime
    action: AuditAction
    resource: str
    resource_id: str | None = None
    user_id: str | None = None
    user_email: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    severity: AuditSeverity = AuditSeverity.LOW
    success: bool = True
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "details": self.details,
            "severity": self.severity.value,
            "success": self.success,
            "error_message": self.error_message,
        }


class AuditLogger:
    """Enterprise audit logging system."""

    def __init__(self, max_entries: int = 10000):
        self._entries: list[AuditEntry] = []
        self._max_entries = max_entries
        self._listeners: list = []

    def log(
        self,
        action: AuditAction,
        resource: str,
        resource_id: str | None = None,
        user_id: str | None = None,
        user_email: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict[str, Any] | None = None,
        severity: AuditSeverity = AuditSeverity.LOW,
        success: bool = True,
        error_message: str | None = None,
    ) -> AuditEntry:
        entry = AuditEntry(
            id=generate_uuid(),
            timestamp=datetime.now(timezone.utc),
            action=action,
            resource=resource,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            severity=severity,
            success=success,
            error_message=error_message,
        )

        self._entries.append(entry)

        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

        for listener in self._listeners:
            try:
                listener(entry)
            except Exception:
                pass

        return entry

    def query(
        self,
        action: AuditAction | None = None,
        resource: str | None = None,
        user_id: str | None = None,
        severity: AuditSeverity | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]:
        entries = self._entries

        if action:
            entries = [e for e in entries if e.action == action]
        if resource:
            entries = [e for e in entries if e.resource == resource]
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if severity:
            entries = [e for e in entries if e.severity == severity]
        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]
        if end_time:
            entries = [e for e in entries if e.timestamp <= end_time]

        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries[offset:offset + limit]

    def get_user_activity(self, user_id: str, limit: int = 50) -> list[AuditEntry]:
        return self.query(user_id=user_id, limit=limit)

    def get_resource_history(self, resource: str, resource_id: str, limit: int = 50) -> list[AuditEntry]:
        entries = [
            e for e in self._entries
            if e.resource == resource and e.resource_id == resource_id
        ]
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]

    def get_security_events(self, limit: int = 100) -> list[AuditEntry]:
        security_actions = {
            AuditAction.LOGIN_FAILED,
            AuditAction.PASSWORD_CHANGE,
            AuditAction.PERMISSION_CHANGE,
            AuditAction.ROLE_CHANGE,
            AuditAction.API_KEY_CREATE,
            AuditAction.API_KEY_REVOKE,
        }
        entries = [e for e in self._entries if e.action in security_actions]
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]

    def get_statistics(self) -> dict[str, Any]:
        if not self._entries:
            return {"total": 0}

        action_counts: dict[str, int] = {}
        resource_counts: dict[str, int] = {}
        severity_counts: dict[str, int] = {}
        user_counts: dict[str, int] = {}

        for entry in self._entries:
            action_counts[entry.action.value] = action_counts.get(entry.action.value, 0) + 1
            resource_counts[entry.resource] = resource_counts.get(entry.resource, 0) + 1
            severity_counts[entry.severity.value] = severity_counts.get(entry.severity.value, 0) + 1
            if entry.user_id:
                user_counts[entry.user_id] = user_counts.get(entry.user_id, 0) + 1

        return {
            "total": len(self._entries),
            "by_action": action_counts,
            "by_resource": resource_counts,
            "by_severity": severity_counts,
            "by_user": user_counts,
            "first_entry": self._entries[0].timestamp.isoformat(),
            "last_entry": self._entries[-1].timestamp.isoformat(),
        }

    def add_listener(self, listener) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener) -> None:
        self._listeners = [l for l in self._listeners if l != listener]

    def export(
        self,
        format: str = "json",
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> str | list[dict]:
        entries = self.query(start_time=start_time, end_time=end_time, limit=len(self._entries))

        if format == "json":
            import json
            return json.dumps([e.to_dict() for e in entries], indent=2)
        elif format == "csv":
            lines = ["id,timestamp,action,resource,resource_id,user_id,severity,success"]
            for e in entries:
                lines.append(
                    f"{e.id},{e.timestamp.isoformat()},{e.action.value},"
                    f"{e.resource},{e.resource_id or ''},{e.user_id or ''},"
                    f"{e.severity.value},{e.success}"
                )
            return "\n".join(lines)
        else:
            return [e.to_dict() for e in entries]

    def clear(self, before: datetime | None = None) -> int:
        if before:
            original_count = len(self._entries)
            self._entries = [e for e in self._entries if e.timestamp >= before]
            return original_count - len(self._entries)
        else:
            count = len(self._entries)
            self._entries.clear()
            return count


audit_logger = AuditLogger()
