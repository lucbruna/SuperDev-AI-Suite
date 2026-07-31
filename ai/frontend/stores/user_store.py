"""
User Store
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class UserState:
    id: str | None = None
    name: str = ""
    email: str = ""
    role: str = "user"
    preferences: dict[str, Any] = field(default_factory=dict)
    is_authenticated: bool = False


class UserStore:
    def __init__(self):
        self.state = UserState()
        self.listeners: list = []

    def set_user(self, user: dict[str, Any]) -> None:
        self.state.id = user.get("id")
        self.state.name = user.get("name", "")
        self.state.email = user.get("email", "")
        self.state.role = user.get("role", "user")
        self.state.is_authenticated = True
        self._notify()

    def logout(self) -> None:
        self.state = UserState()
        self._notify()

    def update_preferences(self, prefs: dict[str, Any]) -> None:
        self.state.preferences.update(prefs)
        self._notify()

    def _notify(self) -> None:
        for cb in self.listeners:
            cb(self.state)

    def on_change(self, callback) -> None:
        self.listeners.append(callback)

    def render(self) -> dict[str, Any]:
        return {"name": self.state.name, "email": self.state.email, "role": self.state.role, "authenticated": self.state.is_authenticated}
