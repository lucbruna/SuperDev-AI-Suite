"""User manager."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class UserManager:
    def __init__(self) -> None:
        self._roles: Dict[str, List[str]] = {"admin": ["*"], "manager": ["read", "write", "manage"], "member": ["read", "write"], "viewer": ["read"]}
        self._assignments: Dict[str, str] = {}
    def assign_role(self, user_id: str, role: str) -> bool:
        self._assignments[user_id] = role
        return True
    def get_role(self, user_id: str) -> str:
        return self._assignments.get(user_id, "viewer")
    def has_permission(self, user_id: str, permission: str) -> bool:
        role = self.get_role(user_id)
        perms = self._roles.get(role, [])
        return "*" in perms or permission in perms
    def list_roles(self) -> Dict[str, List[str]]:
        return dict(self._roles)
    def add_role(self, name: str, permissions: List[str]) -> None:
        self._roles[name] = permissions
    def remove_role(self, name: str) -> bool:
        if name in self._roles and name not in ("admin", "viewer"):
            del self._roles[name]
            return True
        return False
    def list_users_by_role(self, role: str) -> List[str]:
        return [uid for uid, r in self._assignments.items() if r == role]
