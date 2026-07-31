"""Identity engine for user and organization management."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid, time

from .user_identity import UserIdentityManager
from .organization import OrganizationManager
from .account_manager import AccountManager
from .identity_provider import IdentityProviderManager
from .verification import IdentityVerification
from .identity_history import IdentityHistory


class IdentityEngine:
    def __init__(self) -> None:
        self._users = UserIdentityManager()
        self._orgs = OrganizationManager()
        self._accounts = AccountManager()
        self._providers = IdentityProviderManager()
        self._verification = IdentityVerification()
        self._history = IdentityHistory()

    def create_user(self, username: str, email: str, role: str = "viewer") -> Dict[str, Any]:
        uid = str(uuid.uuid4())[:8]
        self._users.create(uid, username, email, role)
        self._history.record(uid, "user_created", {"username": username})
        return {"user_id": uid, "username": username, "status": "created"}

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._users.get(user_id)

    def deactivate_user(self, user_id: str) -> bool:
        result = self._users.deactivate(user_id)
        if result:
            self._history.record(user_id, "user_deactivated", {})
        return result

    def create_organization(self, name: str) -> Dict[str, Any]:
        return self._orgs.create(name)

    def verify_identity(self, user_id: str, method: str = "email") -> Dict[str, Any]:
        return self._verification.verify(user_id, method)

    def get_history(self, user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        return self._history.get(user_id, limit)

    def snapshot(self) -> Dict[str, Any]:
        return {"users": self._users.count(), "orgs": self._orgs.count()}
