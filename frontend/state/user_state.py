from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UserState:
    """Session-local user state."""

    user_id: str | None = None
    name: str = ""
    email: str = ""
    roles: list[str] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)
    authenticated: bool = False

    def login(self, user_id: str, email: str, name: str = "", roles: list[str] | None = None) -> None:
        self.user_id = user_id
        self.email = email
        self.name = name
        self.roles = list(roles or [])
        self.authenticated = True

    def logout(self) -> None:
        self.user_id = None
        self.email = ""
        self.name = ""
        self.roles = []
        self.authenticated = False

    def has_role(self, role: str) -> bool:
        return role in self.roles or "admin" in self.roles

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "roles": list(self.roles),
            "preferences": dict(self.preferences),
            "authenticated": self.authenticated,
        }
