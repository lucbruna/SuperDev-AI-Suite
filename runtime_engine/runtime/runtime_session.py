from __future__ import annotations

import time
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from runtime_engine.core.configuration import RuntimeConfig


class SessionStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class RuntimeSession(BaseModel):
    id: str
    language: str = "python"
    status: SessionStatus = SessionStatus.CREATED
    started_at: datetime | None = None
    finished_at: datetime | None = None
    config: RuntimeConfig = Field(default_factory=RuntimeConfig)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def start(self) -> None:
        self.status = SessionStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self) -> None:
        self.status = SessionStatus.COMPLETED
        self.finished_at = datetime.utcnow()

    def fail(self) -> None:
        self.status = SessionStatus.FAILED
        self.finished_at = datetime.utcnow()

    def timeout(self) -> None:
        self.status = SessionStatus.TIMEOUT
        self.finished_at = datetime.utcnow()

    def cancel(self) -> None:
        self.status = SessionStatus.CANCELLED
        self.finished_at = datetime.utcnow()

    @property
    def duration(self) -> float | None:
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        if self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return None


class RuntimeSessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, RuntimeSession] = {}

    def add(self, session: RuntimeSession) -> None:
        self._sessions[session.id] = session

    def get(self, session_id: str) -> RuntimeSession | None:
        return self._sessions.get(session_id)

    def remove(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def list_all(self) -> list[RuntimeSession]:
        return list(self._sessions.values())

    async def shutdown_all(self) -> None:
        for session in self._sessions.values():
            session.cancel()
        self._sessions.clear()

    def __len__(self) -> int:
        return len(self._sessions)
