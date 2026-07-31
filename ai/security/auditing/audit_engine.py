"""Audit engine."""
from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any


class AuditAction(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS = "access"
    CONFIGURE = "configure"
    EXECUTE = "execute"
    EXPORT = "export"
    ERROR = "error"

class AuditEntry:
    def __init__(self, action: AuditAction, user_id: str, resource: str = "", details: str = "") -> None:
        self.entry_id = str(uuid.uuid4())[:8]
        self.timestamp = time.time()
        self.action = action
        self.user_id = user_id
        self.resource = resource
        self.details = details

class AuditEngine:
    def __init__(self, max_entries: int = 10000) -> None:
        self._entries: list[AuditEntry] = []
        self._max = max_entries
    def log(self, action: AuditAction, user_id: str, resource: str = "", details: str = "") -> AuditEntry:
        entry = AuditEntry(action, user_id, resource, details)
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return entry
    def query(self, user_id: str = "", action: AuditAction | None = None, resource: str = "", limit: int = 100) -> list[AuditEntry]:
        results = self._entries
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        if action:
            results = [e for e in results if e.action == action]
        if resource:
            results = [e for e in results if e.resource == resource]
        return results[-limit:]
    def count(self) -> int:
        return len(self._entries)
    def clear(self) -> int:
        n = len(self._entries)
        self._entries.clear()
        return n
    def export_entries(self, limit: int = 100) -> list[dict[str, Any]]:
        return [{"id": e.entry_id, "ts": e.timestamp, "action": e.action.value, "user": e.user_id, "resource": e.resource, "details": e.details} for e in self._entries[-limit:]]
