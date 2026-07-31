"""Privilege checker."""
from __future__ import annotations

from enum import Enum


class Privilege(Enum):
    VIEW = "view"
    EDIT = "edit"
    CREATE = "create"
    DELETE = "delete"
    EXECUTE = "execute"
    CONFIGURE = "configure"
    AUDIT = "audit"
    ADMIN = "admin"

class PrivilegeChecker:
    def __init__(self) -> None:
        self._grants: dict[str, set[Privilege]] = {}
        self._denials: dict[str, set[Privilege]] = {}
    def grant(self, user_id: str, privilege: Privilege) -> None:
        self._grants.setdefault(user_id, set()).add(privilege)
    def deny(self, user_id: str, privilege: Privilege) -> None:
        self._denials.setdefault(user_id, set()).add(privilege)
    def revoke_grant(self, user_id: str, privilege: Privilege) -> bool:
        if user_id in self._grants:
            self._grants[user_id].discard(privilege)
            return True
        return False
    def revoke_denial(self, user_id: str, privilege: Privilege) -> bool:
        if user_id in self._denials:
            self._denials[user_id].discard(privilege)
            return True
        return False
    def check(self, user_id: str, privilege: Privilege) -> bool:
        if user_id in self._denials and privilege in self._denials[user_id]:
            return False
        return privilege in self._grants.get(user_id, set())
    def get_privileges(self, user_id: str) -> list[str]:
        return [p.value for p in self._grants.get(user_id, set())]
    def check_admin(self, user_id: str) -> bool:
        return self.check(user_id, Privilege.ADMIN)
