"""User engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class UserEngine:
    def __init__(self) -> None:
        self._users: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def create(self, email: str, name: str, org_id: str = "", role: str = "member") -> Dict[str, Any]:
        import uuid
        user_id = str(uuid.uuid4())[:8]
        user = {"id": user_id, "email": email, "name": name, "org_id": org_id, "role": role, "status": "active", "created_at": time.time()}
        self._users[user_id] = user
        return user
    def get(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._users.get(user_id)
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        for u in self._users.values():
            if u.get("email") == email:
                return u
        return None
    def update(self, user_id: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        user = self._users.get(user_id)
        if user:
            user.update(kwargs)
            return user
        return None
    def delete(self, user_id: str) -> bool:
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._users.values())
    def list_by_org(self, org_id: str) -> List[Dict[str, Any]]:
        return [u for u in self._users.values() if u.get("org_id") == org_id]
    def count(self) -> int:
        return len(self._users)
