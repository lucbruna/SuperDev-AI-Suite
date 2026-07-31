"""Authorization engine for RBAC + ABAC."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"

class AuthorizationEngine:
    def __init__(self) -> None:
        self._user_roles: Dict[str, set[str]] = {}
        self._role_permissions: Dict[str, set[Permission]] = {}
        self._resource_policies: Dict[str, Dict[str, Any]] = {}
    def assign_role(self, user_id: str, role: str) -> bool:
        if user_id not in self._user_roles:
            self._user_roles[user_id] = set()
        self._user_roles[user_id].add(role)
        return True
    def grant_permission(self, role: str, permission: Permission) -> bool:
        if role not in self._role_permissions:
            self._role_permissions[role] = set()
        self._role_permissions[role].add(permission)
        return True
    def check_permission(self, user_id: str, permission: Permission, resource: str = "") -> bool:
        roles = self._user_roles.get(user_id, set())
        for role in roles:
            perms = self._role_permissions.get(role, set())
            if Permission.ADMIN in perms or permission in perms:
                return True
        return False
    def revoke_role(self, user_id: str, role: str) -> bool:
        if user_id in self._user_roles:
            self._user_roles[user_id].discard(role)
            return True
        return False
    def get_user_permissions(self, user_id: str) -> List[str]:
        roles = self._user_roles.get(user_id, set())
        perms: set[Permission] = set()
        for role in roles:
            perms |= self._role_permissions.get(role, set())
        return [p.value for p in perms]
    def add_resource_policy(self, resource: str, policy: Dict[str, Any]) -> None:
        self._resource_policies[resource] = policy
    def evaluate_abac(self, user_id: str, resource: str, attributes: Dict[str, Any]) -> bool:
        policy = self._resource_policies.get(resource)
        if not policy:
            return True
        required_roles = policy.get("required_roles", [])
        user_roles = list(self._user_roles.get(user_id, set()))
        if required_roles and not any(r in user_roles for r in required_roles):
            return False
        return True
