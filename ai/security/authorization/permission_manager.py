"""Permission management."""
from __future__ import annotations
from typing import Any, Dict, List, Set
from enum import Enum

class PermissionLevel(Enum):
    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 3
    ADMIN = 4

class PermissionManager:
    def __init__(self) -> None:
        self._permissions: Dict[str, Set[str]] = {}
        self._hierarchy: Dict[str, List[str]] = {}
    def define_permission(self, name: str, parent: str = "") -> None:
        self._permissions[name] = set()
        if parent:
            if parent not in self._hierarchy:
                self._hierarchy[parent] = []
            self._hierarchy[parent].append(name)
    def grant(self, user_id: str, permission: str) -> None:
        if user_id not in self._permissions:
            self._permissions[user_id] = set()
        self._permissions[user_id].add(permission)
        for child in self._hierarchy.get(permission, []):
            self._permissions[user_id].add(child)
    def revoke(self, user_id: str, permission: str) -> bool:
        if user_id in self._permissions:
            self._permissions[user_id].discard(permission)
            return True
        return False
    def check(self, user_id: str, permission: str) -> bool:
        return permission in self._permissions.get(user_id, set())
    def list_permissions(self, user_id: str) -> List[str]:
        return sorted(self._permissions.get(user_id, set()))
    def revoke_all(self, user_id: str) -> None:
        self._permissions.pop(user_id, None)
