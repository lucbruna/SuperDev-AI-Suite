"""
AI Chat Interface
"""
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json


class ChatRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    STREAMING = "streaming"
    ERROR = "error"


@dataclass
class ChatMessage:
    role: ChatRole
    content: str
    id: str = ""
    timestamp: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_streaming: bool = False
    error: Optional[str] = None


@dataclass
class ChatConfig:
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = "You are SuperDev AI Assistant."
    streaming: bool = True
    auto_scroll: bool = True
    max_history: int = 100


class AIChat:
    def __init__(self, config: Optional[ChatConfig] = None):
        self.config = config or ChatConfig()
        self.messages: List[ChatMessage] = []
        self.status = ChatStatus.IDLE
        self.listeners: List[Callable] = []
        
    def send(self, content: str) -> ChatMessage:
        msg = ChatMessage(role=ChatRole.USER, content=content)
        self.messages.append(msg)
        self.status = ChatStatus.THINKING
        self._emit("message_sent", {"message": msg})
        return msg
        
    def receive(self, content: str) -> ChatMessage:
        msg = ChatMessage(role=ChatRole.ASSISTANT, content=content)
        self.messages.append(msg)
        self.status = ChatStatus.IDLE
        self._emit("message_received", {"message": msg})
        return msg
        
    def clear(self) -> None:
        self.messages.clear()
        self.status = ChatStatus.IDLE
        self._emit("conversation_cleared", {})
        
    def on(self, event: str, callback: Callable) -> None:
        self.listeners.append({"event": event, "callback": callback})
        
    def _emit(self, event: str, data: Dict[str, Any]) -> None:
        for l in self.listeners:
            if l["event"] == event:
                l["callback"](data)
                
    def render(self) -> Dict[str, Any]:
        return {
            "messages": [{"role": m.role.value, "content": m.content} for m in self.messages],
            "status": self.status.value,
            "config": {"model": self.config.model, "streaming": self.config.streaming},
        }
