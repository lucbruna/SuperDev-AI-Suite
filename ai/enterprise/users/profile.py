"""User profile."""
from __future__ import annotations
from typing import Any, Dict, Optional

class UserProfile:
    def __init__(self) -> None:
        self._profiles: Dict[str, Dict[str, Any]] = {}
    def create(self, user_id: str, display_name: str = "", avatar_url: str = "", bio: str = "") -> Dict[str, Any]:
        profile = {"user_id": user_id, "display_name": display_name, "avatar_url": avatar_url, "bio": bio, "phone": "", "location": "", "timezone": "America/Sao_Paulo"}
        self._profiles[user_id] = profile
        return profile
    def get(self, user_id: str) -> Dict[str, Any]:
        return self._profiles.get(user_id, {})
    def update(self, user_id: str, **kwargs: Any) -> Dict[str, Any]:
        if user_id in self._profiles:
            self._profiles[user_id].update(kwargs)
            return self._profiles[user_id]
        return self.create(user_id, **kwargs)
    def delete(self, user_id: str) -> bool:
        if user_id in self._profiles:
            del self._profiles[user_id]
            return True
        return False
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._profiles)
