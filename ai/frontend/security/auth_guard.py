"""
Authentication Guard
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class GuardResult(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REDIRECT = "redirect"


@dataclass
class GuardConfig:
    login_url: str = "/login"
    public_paths: list[str] = None

    def __post_init__(self):
        if self.public_paths is None:
            self.public_paths = ["/login", "/register", "/forgot-password"]


class AuthGuard:
    def __init__(self, config: GuardConfig | None = None):
        self.config = config or GuardConfig()
        self.isAuthenticated: bool = False
        self.user: dict[str, Any] | None = None

    def check(self, path: str) -> GuardResult:
        if path in self.config.public_paths:
            return GuardResult.ALLOW
        if self.isAuthenticated:
            return GuardResult.ALLOW
        return GuardResult.REDIRECT

    def login(self, user: dict[str, Any]) -> None:
        self.user = user
        self.isAuthenticated = True

    def logout(self) -> None:
        self.user = None
        self.isAuthenticated = False

    def render(self) -> dict[str, Any]:
        return {"authenticated": self.isAuthenticated, "user": self.user}
