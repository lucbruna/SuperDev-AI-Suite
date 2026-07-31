"""Enterprise security."""
from __future__ import annotations

import time
from typing import Any


class EnterpriseSecurity:
    def __init__(self) -> None:
        self._permissions: dict[str, list[str]] = {}
        self._audit_log: list[dict[str, Any]] = []
        self._rate_limits: dict[str, dict[str, Any]] = {}
    def set_permissions(self, role: str, permissions: list[str]) -> None:
        self._permissions[role] = permissions
    def check_permission(self, role: str, permission: str) -> bool:
        return permission in self._permissions.get(role, [])
    def log_audit(self, user_id: str, action: str, resource: str, details: str = "") -> dict[str, Any]:
        entry = {"user_id": user_id, "action": action, "resource": resource, "details": details, "timestamp": time.time()}
        self._audit_log.append(entry)
        return entry
    def get_audit_log(self, user_id: str = "", action: str = "", limit: int = 100) -> list[dict[str, Any]]:
        results = self._audit_log
        if user_id:
            results = [e for e in results if e["user_id"] == user_id]
        if action:
            results = [e for e in results if e["action"] == action]
        return results[-limit:]
    def set_rate_limit(self, resource: str, max_requests: int, window_seconds: int = 60) -> None:
        self._rate_limits[resource] = {"max_requests": max_requests, "window": window_seconds, "requests": []}
    def check_rate_limit(self, resource: str) -> bool:
        limit = self._rate_limits.get(resource)
        if not limit:
            return True
        now = time.time()
        limit["requests"] = [r for r in limit["requests"] if now - r < limit["window"]]
        if len(limit["requests"]) >= limit["max_requests"]:
            return False
        limit["requests"].append(now)
        return True
    def list_roles(self) -> list[str]:
        return list(self._permissions.keys())
    def get_permissions(self, role: str) -> list[str]:
        return list(self._permissions.get(role, []))
