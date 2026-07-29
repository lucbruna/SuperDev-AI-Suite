"""
Access Control - Granular financial data access control.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class AccessControl:
    def __init__(self, config: FinancialConfig):
        self.config = config
        self._roles = {
            "cfi": {"financial": ["read", "write", "approve", "audit", "configure"]},
            "treasury": {"cashflow": ["read", "write", "approve"], "treasury": ["read", "write", "approve"]},
            "accountant": {"accounting": ["read", "write", "reconcile"], "reporting": ["read"]},
            "auditor": {"*": ["read", "audit"]},
            "manager": {"budget": ["read", "write"], "reporting": ["read"]},
            "viewer": {"*": ["read"]},
        }
        self._users: Dict[str, str] = {}

    async def check(self, user_id: str, resource: str, action: str) -> bool:
        role = self._users.get(user_id)
        if not role:
            return False
        perms = self._roles.get(role, {})
        wildcard = perms.get("*", [])
        if action in wildcard:
            return True
        return action in perms.get(resource, [])

    async def grant(self, user_id: str, role: str) -> None:
        if role in self._roles:
            self._users[user_id] = role
            logger.info(f"Access: {user_id} -> {role}")

    async def revoke(self, user_id: str) -> None:
        self._users.pop(user_id, None)

    async def get_user_permissions(self, user_id: str) -> Dict[str, List[str]]:
        role = self._users.get(user_id)
        return {k: v for k, v in self._roles.get(role, {}).items()}