"""AI Model security."""
from __future__ import annotations
from typing import Any, Dict, List

class ModelSecurity:
    def __init__(self) -> None:
        self._access_control: Dict[str, List[str]] = {}
        self._audit_log: List[Dict[str, Any]] = []
        self._blocked_patterns: List[str] = []
    def set_permissions(self, role: str, permissions: List[str]) -> None:
        self._access_control[role] = permissions
    def check_permission(self, role: str, permission: str) -> bool:
        return permission in self._access_control.get(role, [])
    def log_access(self, user_id: str, model_id: str, action: str) -> None:
        self._audit_log.append({"user_id": user_id, "model_id": model_id, "action": action})
    def add_blocked_pattern(self, pattern: str) -> None:
        self._blocked_patterns.append(pattern)
    def check_prompt(self, prompt: str) -> bool:
        return not any(p.lower() in prompt.lower() for p in self._blocked_patterns)
    def get_audit_log(self, user_id: str = "", model_id: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        results = self._audit_log
        if user_id:
            results = [e for e in results if e["user_id"] == user_id]
        if model_id:
            results = [e for e in results if e["model_id"] == model_id]
        return results[-limit:]
    def list_roles(self) -> List[str]:
        return list(self._access_control.keys())
