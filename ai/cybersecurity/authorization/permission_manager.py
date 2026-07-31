"""
Permission Manager
"""
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field


@dataclass
class Permission:
    name: str
    resource: str = ""
    action: str = ""
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class PermissionManager:
    def __init__(self):
        self.permissions: Dict[str, Permission] = {}
        self.user_permissions: Dict[str, Set[str]] = {}
        self.role_permissions: Dict[str, Set[str]] = {}
        
    def create_permission(self, name: str, resource: str = "", action: str = "", description: str = "") -> Permission:
        perm = Permission(name=name, resource=resource, action=action, description=description)
        self.permissions[name] = perm
        return perm
        
    def get_permission(self, name: str) -> Optional[Permission]:
        return self.permissions.get(name)
        
    def list_permissions(self) -> List[Permission]:
        return list(self.permissions.values())
        
    def grant_to_user(self, user_id: str, permission_name: str) -> bool:
        if permission_name not in self.permissions:
            return False
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = set()
        self.user_permissions[user_id].add(permission_name)
        return True
        
    def revoke_from_user(self, user_id: str, permission_name: str) -> bool:
        if user_id in self.user_permissions:
            self.user_permissions[user_id].discard(permission_name)
            return True
        return False
        
    def grant_to_role(self, role_name: str, permission_name: str) -> bool:
        if permission_name not in self.permissions:
            return False
        if role_name not in self.role_permissions:
            self.role_permissions[role_name] = set()
        self.role_permissions[role_name].add(permission_name)
        return True
        
    def revoke_from_role(self, role_name: str, permission_name: str) -> bool:
        if role_name in self.role_permissions:
            self.role_permissions[role_name].discard(permission_name)
            return True
        return False
        
    def has_permission(self, user_id: str, permission_name: str) -> bool:
        if permission_name in self.user_permissions.get(user_id, set()):
            return True
        return False
        
    def get_user_permissions(self, user_id: str) -> Set[str]:
        return self.user_permissions.get(user_id, set()).copy()
        
    def count(self) -> int:
        return len(self.permissions)
