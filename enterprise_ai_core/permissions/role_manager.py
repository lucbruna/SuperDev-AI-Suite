"""
Role Manager - Manages roles and their permissions
"""

from typing import Any, Dict, List
from uuid import UUID


class RoleManager:
    """Manages roles"""

    def __init__(self):
        self._roles: Dict[UUID, Dict] = {}

    def create_role(self, role_id: UUID, name: str, permissions: List[UUID]) -> None:
        self._roles[role_id] = {"name": name, "permissions": permissions}

    def get_role(self, role_id: UUID) -> Dict:
        return self._roles.get(role_id, {})