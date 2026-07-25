from __future__ import annotations
import uuid
import time
from typing import Any, Optional
from dataclasses import dataclass, field


@dataclass
class AISession:
    id: str = ""
    user_id: str = ""
    provider: str = ""
    model: str = ""
    created_at: float = 0.0
    last_active: float = 0.0
    context_window: int = 4096
    metadata: dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        self.last_active = time.time()


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, AISession] = {}

    def create(self, user_id: str, provider: str = "", model: str = "", context_window: int = 4096, metadata: Optional[dict] = None) -> AISession:
        now = time.time()
        session = AISession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider=provider,
            model=model,
            created_at=now,
            last_active=now,
            context_window=context_window,
            metadata=metadata or {},
        )
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Optional[AISession]:
        session = self._sessions.get(session_id)
        if session:
            session.touch()
        return session

    def update(self, session_id: str, **kwargs: Any) -> Optional[AISession]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        session.touch()
        return session

    def delete(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def cleanup_expired(self, max_age: float = 86400) -> int:
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if now - s.last_active > max_age]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)

    def list_by_user(self, user_id: str) -> list[AISession]:
        return [s for s in self._sessions.values() if s.user_id == user_id]
