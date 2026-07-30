from __future__ import annotations

from typing import Any


class PermissionsAnalyzer:
    """Analyzes role-based permissions and access control."""

    def __init__(self) -> None:
        self._roles: dict[str, dict[str, Any]] = {}

    def add_role(self, name: str, permissions: list[str]) -> str:
        self._roles[name] = {
            "name": name,
            "permissions": permissions,
        }
        return name

    def get_role(self, name: str) -> dict[str, Any] | None:
        return self._roles.get(name)

    def remove_role(self, name: str) -> bool:
        if name in self._roles:
            del self._roles[name]
            return True
        return False

    def list_roles(self) -> list[dict[str, Any]]:
        return list(self._roles.values())

    @property
    def role_count(self) -> int:
        return len(self._roles)

    def check_access(self, role: str, required_permission: str) -> bool:
        r = self._roles.get(role)
        if r is None:
            return False
        return required_permission in r["permissions"]

    def analyze_least_privilege(self, grants: list[str]) -> list[str]:
        suggestions = []
        common_grants = {"admin", "superuser", "root", "*", "all"}
        for grant in grants:
            if grant.lower() in common_grants:
                suggestions.append(f"'{grant}' is overly permissive; use scoped permissions instead")
        return suggestions

    def to_dict(self) -> dict[str, Any]:
        return {
            "roles": list(self._roles.values()),
            "role_count": self.role_count,
        }
