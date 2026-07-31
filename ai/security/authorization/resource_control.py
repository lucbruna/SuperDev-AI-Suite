"""Resource access control."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum

class ResourceType(Enum):
    FILE = "file"
    DATABASE = "database"
    API = "api"
    SERVICE = "service"
    AGENT = "agent"
    MODEL = "model"
    MEMORY = "memory"

class ResourceControl:
    def __init__(self) -> None:
        self._resources: Dict[str, Dict[str, Any]] = {}
        self._access_list: Dict[str, Dict[str, List[str]]] = {}
    def register_resource(self, resource_id: str, resource_type: ResourceType, owner: str = "") -> Dict[str, Any]:
        self._resources[resource_id] = {"type": resource_type.value, "owner": owner, "active": True}
        self._access_list[resource_id] = {"read": [], "write": [], "admin": []}
        return {"resource_id": resource_id, "type": resource_type.value, "status": "registered"}
    def grant_access(self, resource_id: str, user_id: str, level: str = "read") -> bool:
        if resource_id not in self._access_list:
            return False
        if level in self._access_list[resource_id]:
            if user_id not in self._access_list[resource_id][level]:
                self._access_list[resource_id][level].append(user_id)
            return True
        return False
    def revoke_access(self, resource_id: str, user_id: str, level: str = "read") -> bool:
        if resource_id in self._access_list and level in self._access_list[resource_id]:
            if user_id in self._access_list[resource_id][level]:
                self._access_list[resource_id][level].remove(user_id)
                return True
        return False
    def check_access(self, resource_id: str, user_id: str, level: str = "read") -> bool:
        if resource_id not in self._access_list:
            return False
        users = self._access_list[resource_id].get(level, [])
        return user_id in users
    def get_resource_users(self, resource_id: str) -> Dict[str, List[str]]:
        return self._access_list.get(resource_id, {})
    def delete_resource(self, resource_id: str) -> bool:
        if resource_id in self._resources:
            del self._resources[resource_id]
            self._access_list.pop(resource_id, None)
            return True
        return False
