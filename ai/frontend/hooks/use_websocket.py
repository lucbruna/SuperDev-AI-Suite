"""
useWebSocket Hook
"""
from typing import Optional, Callable, Dict, Any


class UseWebSocket:
    def __init__(self):
        self.connected: bool = False
        self.listeners: Dict[str, list] = {}
        
    def connect(self, url: str) -> None:
        self.connected = True
        
    def disconnect(self) -> None:
        self.connected = False
        
    def send(self, event: str, data: Any) -> None:
        pass
        
    def on(self, event: str, callback: Callable) -> None:
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
        
    def render(self) -> Dict[str, Any]:
        return {"connected": self.connected}
