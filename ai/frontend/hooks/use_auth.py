"""
useAuth Hook
"""
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class AuthState:
    user: Optional[Dict[str, Any]] = None
    isAuthenticated: bool = False
    loading: bool = False
    error: Optional[str] = None


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
        
    def get_user(self) -> Optional[Dict[str, Any]]:
        return self.state.user
        
    def render(self) -> Dict[str, Any]:
        return {"user": self.state.user, "isAuthenticated": self.state.isAuthenticated, "loading": self.state.loading}
