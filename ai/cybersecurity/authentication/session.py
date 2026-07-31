"""
Session Manager
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid


@dataclass
class Session:
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_accessed: datetime = field(default_factory=datetime.now)
    ip_address: str = ""
    user_agent: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    @property
    def is_expired(self) -> bool:
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False
    
    def touch(self) -> None:
        self.last_accessed = datetime.now()
        
    def invalidate(self) -> None:
        self.is_active = False


class SessionManager:
    def __init__(self, timeout_seconds: int = 3600):
        self.sessions: Dict[str, Session] = {}
        self.timeout = timeout_seconds
        
    def create(self, user_id: str, **kwargs) -> Session:
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            expires_at=datetime.now() + timedelta(seconds=self.timeout),
            **kwargs
        )
        self.sessions[session.session_id] = session
        return session
        
    def get(self, session_id: str) -> Optional[Session]:
        session = self.sessions.get(session_id)
        if session and session.is_active and not session.is_expired:
            session.touch()
            return session
        return None
        
    def destroy(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session:
            session.invalidate()
            return True
        return False
        
    def destroy_all_user(self, user_id: str) -> int:
        count = 0
        for session in self.sessions.values():
            if session.user_id == user_id and session.is_active:
                session.invalidate()
                count += 1
        return count
        
    def get_user_sessions(self, user_id: str) -> List[Session]:
        return [s for s in self.sessions.values() if s.user_id == user_id and s.is_active]
        
    def cleanup_expired(self) -> int:
        expired = [sid for sid, s in self.sessions.items() if s.is_expired]
        for sid in expired:
            del self.sessions[sid]
        return len(expired)
        
    def count(self) -> int:
        return sum(1 for s in self.sessions.values() if s.is_active)
