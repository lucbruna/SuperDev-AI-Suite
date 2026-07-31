"""
Authentication Engine
"""

import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AuthSession:
    session_id: str
    user_id: str
    token: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    ip_address: str = ""
    user_agent: str = ""
    is_active: bool = True

    @property
    def is_expired(self) -> bool:
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False


class AuthEngine:
    def __init__(self):
        self.sessions: dict[str, AuthSession] = {}
        self.failed_attempts: dict[str, int] = {}
        self.locked_accounts: dict[str, datetime] = {}

    def create_session(self, user_id: str, ip_address: str = "", user_agent: str = "") -> AuthSession:
        token = secrets.token_hex(32)
        session = AuthSession(
            session_id=str(uuid.uuid4()), user_id=user_id, token=token, ip_address=ip_address, user_agent=user_agent
        )
        self.sessions[session.session_id] = session
        return session

    def validate_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if not session:
            return False
        return not (not session.is_active or session.is_expired)

    def invalidate_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session:
            session.is_active = False
            return True
        return False

    def record_failed_attempt(self, user_id: str) -> int:
        self.failed_attempts[user_id] = self.failed_attempts.get(user_id, 0) + 1
        return self.failed_attempts[user_id]

    def reset_failed_attempts(self, user_id: str) -> None:
        self.failed_attempts.pop(user_id, None)

    def lock_account(self, user_id: str, duration_seconds: int = 300) -> None:
        from datetime import timedelta

        self.locked_accounts[user_id] = datetime.now() + timedelta(seconds=duration_seconds)

    def is_locked(self, user_id: str) -> bool:
        lock_time = self.locked_accounts.get(user_id)
        if lock_time:
            if datetime.now() < lock_time:
                return True
            del self.locked_accounts[user_id]
        return False

    def count_active_sessions(self) -> int:
        return sum(1 for s in self.sessions.values() if s.is_active and not s.is_expired)
