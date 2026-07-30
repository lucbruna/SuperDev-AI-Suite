from __future__ import annotations

from typing import Any


class Scope:
    """OAuth-style scope definition."""

    def __init__(self, name: str, description: str = "", permissions: list[str] | None = None) -> None:
        self.name = name
        self.description = description
        self._permissions = set(permissions or [])

    def includes(self, permission: str) -> bool:
        if "*" in self._permissions:
            return True
        if permission in self._permissions:
            return True
        for p in self._permissions:
            if p.endswith(":*") and permission.startswith(p[:-1]):
                return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
        }


class ScopeRegistry:
    """Registry for scopes with hierarchy support."""

    def __init__(self) -> None:
        self._scopes: dict[str, Scope] = {}
        self._scope_hierarchy: dict[str, set[str]] = {}

    def register(self, scope: Scope) -> None:
        self._scopes[scope.name] = scope

    def define_hierarchy(self, parent: str, child: str) -> None:
        if parent not in self._scope_hierarchy:
            self._scope_hierarchy[parent] = set()
        self._scope_hierarchy[parent].add(child)

    def get(self, name: str) -> Scope | None:
        return self._scopes.get(name)

    def get_effective_scopes(self, scope_string: str) -> set[str]:
        requested = {s.strip() for s in scope_string.split() if s.strip()}
        effective = set(requested)
        for scope in list(requested):
            effective.update(self._get_descendants(scope))
        return effective

    def _get_descendants(self, scope_name: str) -> set[str]:
        result: set[str] = set()
        children = self._scope_hierarchy.get(scope_name, set())
        for child in children:
            result.add(child)
            result.update(self._get_descendants(child))
        return result

    async def validate_scope(self, scope_string: str, required_scopes: list[str]) -> bool:
        effective = self.get_effective_scopes(scope_string)
        for required in required_scopes:
            if not self._check_scope_grants(effective, required):
                return False
        return True

    def _check_scope_grants(self, effective_scopes: set[str], required: str) -> bool:
        if required in effective_scopes:
            return True
        for scope in effective_scopes:
            if scope.endswith(":*") and required.startswith(scope[:-1]):
                return True
        return False

    def list_scopes(self) -> list[str]:
        return list(self._scopes.keys())

    def to_dict(self) -> dict[str, Any]:
        return {
            "scopes": self.list_scopes(),
            "count": len(self._scopes),
        }
