from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set


class MemoryAction(Enum):
    """Actions that can be performed on memory."""
    READ = auto()
    WRITE = auto()
    UPDATE = auto()
    DELETE = auto()
    MANAGE = auto()
    BACKUP = auto()
    RESTORE = auto()
    CONFIGURE = auto()


class MemoryRole(Enum):
    """Predefined permission roles."""
    NONE = auto()
    READER = auto()
    WRITER = auto()
    OPERATOR = auto()
    ADMIN = auto()
    SYSTEM = auto()


_ROLE_PERMISSIONS: Dict[MemoryRole, Set[MemoryAction]] = {
    MemoryRole.NONE: set(),
    MemoryRole.READER: {MemoryAction.READ},
    MemoryRole.WRITER: {MemoryAction.READ, MemoryAction.WRITE, MemoryAction.UPDATE},
    MemoryRole.OPERATOR: {
        MemoryAction.READ, MemoryAction.WRITE, MemoryAction.UPDATE,
        MemoryAction.DELETE, MemoryAction.BACKUP, MemoryAction.RESTORE,
    },
    MemoryRole.ADMIN: {
        MemoryAction.READ, MemoryAction.WRITE, MemoryAction.UPDATE,
        MemoryAction.DELETE, MemoryAction.BACKUP, MemoryAction.RESTORE,
        MemoryAction.MANAGE, MemoryAction.CONFIGURE,
    },
    MemoryRole.SYSTEM: {
        MemoryAction.READ, MemoryAction.WRITE, MemoryAction.UPDATE,
        MemoryAction.DELETE, MemoryAction.MANAGE, MemoryAction.BACKUP,
        MemoryAction.RESTORE, MemoryAction.CONFIGURE,
    },
}


class MemoryPermissions:
    """Permission management for the memory subsystem."""

    def __init__(self):
        self._role_assignments: Dict[str, MemoryRole] = {}
        self._custom_policies: Dict[str, Set[MemoryAction]] = {}

    def assign_role(self, user: str, role: MemoryRole) -> None:
        self._role_assignments[user] = role

    def get_role(self, user: str) -> MemoryRole:
        return self._role_assignments.get(user, MemoryRole.NONE)

    def remove_user(self, user: str) -> bool:
        return self._role_assignments.pop(user, None) is not None

    def set_custom_policy(self, user: str, actions: Set[MemoryAction]) -> None:
        self._custom_policies[user] = actions

    def get_custom_policy(self, user: str) -> Set[MemoryAction] | None:
        return self._custom_policies.get(user)

    def can(self, user: str, action: MemoryAction) -> bool:
        if user in self._custom_policies:
            return action in self._custom_policies[user]
        role = self._role_assignments.get(user, MemoryRole.NONE)
        return action in _ROLE_PERMISSIONS.get(role, set())

    def can_read(self, user: str) -> bool:
        return self.can(user, MemoryAction.READ)

    def can_write(self, user: str) -> bool:
        return self.can(user, MemoryAction.WRITE)

    def can_update(self, user: str) -> bool:
        return self.can(user, MemoryAction.UPDATE)

    def can_delete(self, user: str) -> bool:
        return self.can(user, MemoryAction.DELETE)

    def can_manage(self, user: str) -> bool:
        return self.can(user, MemoryAction.MANAGE)

    def can_backup(self, user: str) -> bool:
        return self.can(user, MemoryAction.BACKUP)

    def can_restore(self, user: str) -> bool:
        return self.can(user, MemoryAction.RESTORE)

    def list_users(self) -> List[str]:
        return list(self._role_assignments.keys())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "roles": {k: v.name for k, v in self._role_assignments.items()},
            "custom_policies": {
                k: [a.name for a in v]
                for k, v in self._custom_policies.items()
            },
        }
