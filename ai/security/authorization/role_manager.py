"""Role management."""
from __future__ import annotations

from typing import Any


class RoleManager:
    def __init__(self) -> None:
        self._roles: dict[str, dict[str, Any]] = {}
        self._role_hierarchies: dict[str, set[str]] = {}
        self._user_roles: dict[str, set[str]] = {}
    def create_role(self, name: str, description: str = "", parent: str = "") -> dict[str, Any]:
        self._roles[name] = {"name": name, "description": description, "active": True}
        if parent and parent in self._roles:
            self._role_hierarchies[name] = {parent}
            self._role_hierarchies.setdefault(parent, set()).add(name)
        return self._roles[name]
    def assign_role(self, user_id: str, role: str) -> bool:
        if role not in self._roles:
            return False
        self._user_roles.setdefault(user_id, set()).add(role)
        return True
    def revoke_role(self, user_id: str, role: str) -> bool:
        if user_id in self._user_roles:
            self._user_roles[user_id].discard(role)
            return True
        return False
    def get_user_roles(self, user_id: str) -> list[str]:
        return sorted(self._user_roles.get(user_id, set()))
    def get_role_permissions(self, role: str) -> list[str]:
        parents = self._role_hierarchies.get(role, set())
        return sorted(parents)
    def deactivate_role(self, name: str) -> bool:
        if name in self._roles:
            self._roles[name]["active"] = False
            return True
        return False
    def list_roles(self) -> list[str]:
        return [r for r, v in self._roles.items() if v.get("active")]
