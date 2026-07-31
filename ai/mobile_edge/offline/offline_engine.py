"""Offline Engine - Core offline mode management."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class OfflineMode(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SYNCING = "syncing"
    ERROR = "error"


@dataclass
class OfflineSession:
    session_id: str
    device_id: str
    mode: OfflineMode = OfflineMode.ACTIVE
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    actions_queued: int = 0
    data_cached: float = 0.0


class OfflineEngine:
    def __init__(self):
        self.sessions: Dict[str, OfflineSession] = {}
        self.queue: List[Dict[str, Any]] = []
        self.cache_size_mb: float = 0.0
        self.max_cache_mb: float = 500.0

    def enter_offline(self, device_id: str) -> OfflineSession:
        session_id = hashlib.sha256(f"{device_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        session = OfflineSession(session_id=session_id, device_id=device_id)
        self.sessions[session_id] = session
        return session

    def exit_offline(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session:
            session.mode = OfflineMode.INACTIVE
            session.ended_at = datetime.now()
            return True
        return False

    def queue_action(self, action: Dict[str, Any]) -> None:
        self.queue.append({**action, "queued_at": datetime.now().isoformat()})

    def get_queue(self) -> List[Dict[str, Any]]:
        return list(self.queue)

    def process_queue(self) -> List[Dict[str, Any]]:
        processed = list(self.queue)
        self.queue.clear()
        return processed

    def cache_data(self, key: str, data: Any, size_mb: float = 0.1) -> bool:
        if self.cache_size_mb + size_mb > self.max_cache_mb:
            return False
        self.cache_size_mb += size_mb
        return True

    def get_session(self, session_id: str) -> Optional[OfflineSession]:
        return self.sessions.get(session_id)

    def get_active_sessions(self) -> List[OfflineSession]:
        return [s for s in self.sessions.values() if s.mode == OfflineMode.ACTIVE]

    def count(self) -> int:
        return len(self.sessions)
