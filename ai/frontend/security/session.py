"""
Session Manager
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SessionData:
    user_id: str = ""
    token: str = ""
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False


class SessionManager:
    def __init__(self):
        self.session: Optional[SessionData] = None
        self.storage_key: str = "superdev_session"
        
    def create(self, user_id: str, token: str, expires_in: int = 3600) -> SessionData:
        from datetime import timedelta
        self.session = SessionData(
            user_id=user_id,
            token=token,
            expires_at=datetime.now() + timedelta(seconds=expires_in)
        )
        return self.session
        
    def get(self) -> Optional[SessionData]:
        if self.session and self.session.is_expired:
            self.destroy()
        return self.session
        
    def destroy(self) -> None:
        self.session = None
        
    def is_valid(self) -> bool:
        return self.session is not None and not self.session.is_expired
        
    def render(self) -> Dict[str, Any]:
        return {"valid": self.is_valid(), "userId": self.session.user_id if self.session else None}
