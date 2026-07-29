"""
Access Control - Granular access control for supply chain resources.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class AccessControl:
    def __init__(self, config: SupplyChainConfig):
        self.config = config
        self._roles = {
            "admin": {"*": ["read", "write", "delete", "approve", "configure"]},
            "manager": {"inventory": ["read", "write"], "procurement": ["read", "write", "approve"],
                        "suppliers": ["read"], "logistics": ["read", "write"]},
            "buyer": {"procurement": ["read", "write"], "suppliers": ["read"]},
            "analyst": {"*": ["read"]},
        }
        self._users: Dict[str, str] = {}

    async def check(self, user_id: str, resource: str, action: str) -> bool:
        role = self._users.get(user_id)
        if not role:
            return False
        permissions = self._roles.get(role, {})
        wildcard = permissions.get("*", [])
        if action in wildcard:
            return True
        resource_perms = permissions.get(resource, [])
        return action in resource_perms

    async def grant_role(self, user_id: str, role: str) -> None:
        if role in self._roles:
            self._users[user_id] = role
            logger.info(f"Access granted: {user_id} -> {role}")

    async def revoke_access(self, user_id: str) -> None:
        self._users.pop(user_id, None)

    async def get_user_permissions(self, user_id: str) -> Dict[str, List[str]]:
        role = self._users.get(user_id)
        perms = self._roles.get(role, {})
        return {k: v for k, v in perms.items()}