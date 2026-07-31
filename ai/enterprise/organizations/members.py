"""Organization members."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class MemberManager:
    def __init__(self) -> None:
        self._memberships: Dict[str, Dict[str, Dict[str, Any]]] = {}
    def add(self, org_id: str, user_id: str, role: str = "member") -> Dict[str, Any]:
        membership = {"org_id": org_id, "user_id": user_id, "role": role, "joined_at": time.time(), "active": True}
        self._memberships.setdefault(org_id, {})[user_id] = membership
        return membership
    def remove(self, org_id: str, user_id: str) -> bool:
        if org_id in self._memberships and user_id in self._memberships[org_id]:
            del self._memberships[org_id][user_id]
            return True
        return False
    def get(self, org_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return self._memberships.get(org_id, {}).get(user_id)
    def list_members(self, org_id: str) -> List[Dict[str, Any]]:
        return list(self._memberships.get(org_id, {}).values())
    def count(self, org_id: str) -> int:
        return len(self._memberships.get(org_id, {}))
    def update_role(self, org_id: str, user_id: str, new_role: str) -> bool:
        member = self._memberships.get(org_id, {}).get(user_id)
        if member:
            member["role"] = new_role
            return True
        return False
    def list_by_role(self, org_id: str, role: str) -> List[Dict[str, Any]]:
        return [m for m in self._memberships.get(org_id, {}).values() if m["role"] == role]
