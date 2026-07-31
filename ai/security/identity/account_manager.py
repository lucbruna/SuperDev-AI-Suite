"""Account lifecycle management."""
from __future__ import annotations
from typing import Any, Dict, Optional
import time

class AccountManager:
    def __init__(self) -> None:
        self._accounts: Dict[str, Dict[str, Any]] = {}
    def create(self, user_id: str, account_type: str = "standard") -> Dict[str, Any]:
        acct = {"user_id": user_id, "type": account_type, "status": "active", "created_at": time.time()}
        self._accounts[user_id] = acct
        return acct
    def suspend(self, user_id: str) -> bool:
        if user_id in self._accounts:
            self._accounts[user_id]["status"] = "suspended"
            return True
        return False
    def reactivate(self, user_id: str) -> bool:
        if user_id in self._accounts:
            self._accounts[user_id]["status"] = "active"
            return True
        return False
    def get(self, user_id: str) -> Optional[Dict[str, Any]]:
        return dict(self._accounts[user_id]) if user_id in self._accounts else None
