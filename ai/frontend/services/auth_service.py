"""
Authentication Service
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str
    expires_at: datetime


class AuthService:
    def __init__(self):
        self.tokens: AuthTokens | None = None
        self.user: dict[str, Any] | None = None

    def login(self, email: str, password: str) -> bool:
        self.tokens = AuthTokens(access_token="token", refresh_token="refresh", expires_at=datetime.now())
        return True

    def logout(self) -> None:
        self.tokens = None
        self.user = None

    def is_authenticated(self) -> bool:
        return self.tokens is not None

    def refresh(self) -> bool:
        return True

    def render(self) -> dict[str, Any]:
        return {"authenticated": self.is_authenticated(), "user": self.user}
