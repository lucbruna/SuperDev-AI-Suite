"""
useApi Hook
"""
from typing import Optional, Any, Dict, Callable
from dataclasses import dataclass


@dataclass
class ApiState:
    data: Any = None
    loading: bool = False
    error: Optional[str] = None


class UseApi:
    def __init__(self):
        self.state = ApiState()
        
    def request(self, method: str, url: str, data: Any = None) -> bool:
        self.state.loading = True
        self.state.error = None
        return True
        
    def get(self, url: str) -> bool:
        return self.request("GET", url)
        
    def post(self, url: str, data: Any = None) -> bool:
        return self.request("POST", url, data)
        
    def render(self) -> Dict[str, Any]:
        return {"data": self.state.data, "loading": self.state.loading, "error": self.state.error}
