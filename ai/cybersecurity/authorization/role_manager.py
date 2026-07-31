"""
Role Manager
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class Role:
    name: str
    description: str = ""
    permissions: List[str] = field(default_factory=list)
    parent_role: Optional[str] = None
    is_system: bool = False


class RoleManager:
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, List[str]] = {}
        
    def create_role(self, name: str, description: str = "", permissions: List[str] = None) -> Role:
        role = Role(name=name, description=description, permissions=permissions or [])
        self.roles[name] = role
        return role
        
    def get_role(self, name: str) -> Optional[Role]:
        return self.roles.get(name)
        
    def delete_role(self, name: str) -> bool:
        role = self.roles.get(name)
        if role and not role.is_system:
            del self.roles[name]
            return True
        return False
        
    def list_roles(self) -> List[Role]:
        return list(self.roles.values())
        
    def assign_role(self, user_id: str, role_name: str) -> bool:
        if role_name not in self.roles:
            return False
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        if role_name not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role_name)
        return True
        
    def revoke_role(self, user_id: str, role_name: str) -> bool:
        if user_id in self.user_roles:
            if role_name in self.user_roles[user_id]:
                self.user_roles[user_id].remove(role_name)
                return True
        return False
        
    def get_user_roles(self, user_id: str) -> List[str]:
        return self.user_roles.get(user_id, [])
        
    def get_role_permissions(self, role_name: str) -> List[str]:
        role = self.roles.get(role_name)
        return role.permissions if role else []
        
    def get_user_permissions(self, user_id: str) -> List[str]:
        permissions = set()
        for role_name in self.get_user_roles(user_id):
            permissions.update(self.get_role_permissions(role_name))
        return list(permissions)
        
    def has_role(self, user_id: str, role_name: str) -> bool:
        return role_name in self.get_user_roles(user_id)
        
    def count(self) -> int:
        return len(self.roles)
