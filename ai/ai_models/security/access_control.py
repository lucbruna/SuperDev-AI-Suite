"""Access control."""
from __future__ import annotations
from typing import Any, Dict, List

class AccessController:
    def __init__(self) -> None:
        self._roles: Dict[str, List[str]] = {}
        self._permissions: Dict[str, List[str]] = {}
        self._grants: List[Dict[str, Any]] = []
    def define_role(self, role: str, permissions: List[str]) -> Dict[str, Any]:
        self._roles[role] = permissions
        return {"role": role, "permissions": permissions}
    def check_permission(self, role: str, permission: str) -> bool:
        perms = self._roles.get(role, [])
        return permission in perms or "*" in perms
    def grant(self, user: str, role: str, resource: str) -> Dict[str, Any]:
        grant = {"user": user, "role": role, "resource": resource}
        self._grants.append(grant)
        self._permissions.setdefault(user, []).append(role)
        return grant
    def revoke(self, user: str, role: str) -> bool:
        original = len(self._grants)
        self._grants = [g for g in self._grants if not (g["user"] == user and g["role"] == role)]
        return len(self._grants) < original
    def get_user_roles(self, user: str) -> List[str]:
        return list(set(g["role"] for g in self._grants if g["user"] == user))
    def list_roles(self) -> List[str]:
        return list(self._roles.keys())
    def list_grants(self, user: str = "") -> List[Dict[str, Any]]:
        if user:
            return [g for g in self._grants if g["user"] == user]
        return self._grants
    def count(self) -> int:
        return len(self._grants)
