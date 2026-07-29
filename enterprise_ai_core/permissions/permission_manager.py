"""
Permission Manager - Manages permissions
"""

from typing import Any, Dict, List
from uuid import UUID


class PermissionManager:
    """Manages permissions"""

    def __init__(self):
        self._permissions: Dict[UUID, Dict] = {}

    def grant(self, permission_id: UUID, user_id: UUID, resource: str, action: str) -> None:
        self._permissions[permission_id] = {
            "user_id": user_id,
            "resource": resource,
            "action": action,
        }

    def check(self, user_id: UUID, resource: str, action: str) -> bool:
        return True