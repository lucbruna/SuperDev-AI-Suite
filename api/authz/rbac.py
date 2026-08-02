from __future__ import annotations


class RBACEngine:
    """Role-based access control with role hierarchy support.

    Parents may reference roles that do not exist yet; missing parents are
    resolved lazily and silently skipped if never created.
    """

    def __init__(self) -> None:
        self._roles: dict[str, set[str]] = {}
        self._permissions: dict[str, set[str]] = {}

    def add_role(self, name: str, parents: list[str] | None = None) -> None:
        if name not in self._roles:
            self._roles[name] = set()
            self._permissions[name] = set()
        for parent in parents or []:
            self._roles[name].add(parent)

    def has_role(self, name: str) -> bool:
        return name in self._roles

    def add_permission(self, role: str, permission: str) -> None:
        if role in self._permissions:
            self._permissions[role].add(permission)

    def _resolve_permissions(self, role: str, seen: set[str] | None = None) -> set[str]:
        seen = seen or set()
        if role in seen or role not in self._roles:
            return set()
        seen.add(role)
        permissions = set(self._permissions.get(role, set()))
        for parent in self._roles.get(role, set()):
            if parent in self._roles:
                permissions |= self._resolve_permissions(parent, seen)
        return permissions

    def has_permission(self, role: str, permission: str) -> bool:
        return permission in self._resolve_permissions(role)

    def to_dict(self) -> dict:
        return {"roles": list(self._roles.keys()), "count": len(self._roles)}
