from __future__ import annotations

from typing import Any


class ReasoningPermissions:
    """Permission management for reasoning operations."""

    def __init__(self):
        self._permissions: dict[str, set[str]] = {}

    def grant(self, role: str, action: str) -> None:
        if role not in self._permissions:
            self._permissions[role] = set()
        self._permissions[role].add(action)

    def revoke(self, role: str, action: str) -> None:
        if role in self._permissions:
            self._permissions[role].discard(action)

    def can(self, role: str, action: str) -> bool:
        return action in self._permissions.get(role, set())

    def list_roles(self) -> list[str]:
        return list(self._permissions.keys())

    def list_actions(self, role: str) -> list[str]:
        return list(self._permissions.get(role, set()))
