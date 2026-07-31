"""
User Store
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class UserState:
    id: Optional[str] = None
    name: str = ""
    email: str = ""
    role: str = "user"
    preferences: Dict[str, Any] = field(default_factory=dict)
    is_authenticated: bool = False


class UserStore:
    def __init__(self):
        self.state = UserState()
        self.listeners: List = []
        
    def set_user(self, user: Dict[str, Any]) -> None:
        self.state.id = user.get("id")
        self.state.name = user.get("name", "")
        self.state.email = user.get("email", "")
        self.state.role = user.get("role", "user")
        self.state.is_authenticated = True
        self._notify()
        
    def logout(self) -> None:
        self.state = UserState()
        self._notify()
        
    def update_preferences(self, prefs: Dict[str, Any]) -> None:
        self.state.preferences.update(prefs)
        self._notify()
        
    def _notify(self) -> None:
        for cb in self.listeners:
            cb(self.state)
            
    def on_change(self, callback) -> None:
        self.listeners.append(callback)
        
    def render(self) -> Dict[str, Any]:
        return {"name": self.state.name, "email": self.state.email, "role": self.state.role, "authenticated": self.state.is_authenticated}
