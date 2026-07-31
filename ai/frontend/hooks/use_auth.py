"""
useAuth Hook
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class AuthState:
    user: dict[str, Any] | None = None
    isAuthenticated: bool = False
    loading: bool = False
    error: str | None = None


class UseAuth:
    def __init__(self):
        self.state = AuthState()
        self.listeners: list = []

    def login(self, email: str, password: str) -> bool:
        self.state.loading = True
        self.state.error = None
        return True

    def logout(self) -> None:
        self.state = AuthState()

    def get_user(self) -> dict[str, Any] | None:
        return self.state.user

    def render(self) -> dict[str, Any]:
        return {"user": self.state.user, "isAuthenticated": self.state.isAuthenticated, "loading": self.state.loading}
