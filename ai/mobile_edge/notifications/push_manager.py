"""Push Manager - Push notification management."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class PushToken:
    token_id: str
    device_id: str
    platform: str = ""
    token: str = ""
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PushMessage:
    message_id: str
    title: str
    body: str
    data: dict[str, Any] = field(default_factory=dict)
    token_ids: list[str] = field(default_factory=list)
    sent_at: datetime | None = None
    success_count: int = 0
    failure_count: int = 0


class PushManager:
    def __init__(self):
        self.tokens: dict[str, PushToken] = {}
        self.messages: list[PushMessage] = []

    def register_token(self, device_id: str, platform: str, token: str) -> PushToken:
        token_id = hashlib.sha256(f"{device_id}{token}".encode()).hexdigest()[:16]
        push_token = PushToken(token_id=token_id, device_id=device_id, platform=platform, token=token)
        self.tokens[token_id] = push_token
        return push_token

    def unregister_token(self, token_id: str) -> bool:
        if token_id in self.tokens:
            self.tokens[token_id].active = False
            return True
        return False

    def send_push(self, title: str, body: str, token_ids: list[str] = None, data: dict[str, Any] = None) -> PushMessage:
        msg_id = hashlib.sha256(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        if not token_ids:
            token_ids = [t.token_id for t in self.tokens.values() if t.active]
        msg = PushMessage(message_id=msg_id, title=title, body=body, data=data or {}, token_ids=token_ids, sent_at=datetime.now(), success_count=len(token_ids))
        self.messages.append(msg)
        return msg

    def get_tokens(self, device_id: str = None) -> list[PushToken]:
        tokens = list(self.tokens.values())
        if device_id:
            tokens = [t for t in tokens if t.device_id == device_id]
        return tokens

    def get_messages(self, limit: int = 100) -> list[PushMessage]:
        return self.messages[-limit:]

    def count(self) -> int:
        return len(self.messages)
