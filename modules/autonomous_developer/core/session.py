"""Developer sessions — scoped autonomous executions.

A session groups one task run: its goal, statistics and events. The session
manager keeps active sessions and a bounded history of closed ones so the API
can expose "last run" and "running run" views.
"""
from __future__ import annotations

import logging
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DeveloperSession:
    """A single autonomous developer execution."""

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    project_root: str = ""
    status: str = "created"  # created | running | completed | failed | cancelled
    goal: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def elapsed_seconds(self) -> float:
        end = self.finished_at or time.time()
        return round(end - self.created_at, 3)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "elapsed_seconds": self.elapsed_seconds,
            "project_root": self.project_root,
            "status": self.status,
            "goal": self.goal,
            "meta": self.meta,
        }


class SessionManager:
    """Tracks active and recently closed developer sessions."""

    def __init__(self, history_limit: int = 50) -> None:
        self._history: deque[DeveloperSession] = deque(maxlen=history_limit)
        self._active: dict[str, DeveloperSession] = {}

    def create(
        self,
        project_root: str = "",
        goal: str = "",
        meta: dict[str, Any] | None = None,
    ) -> DeveloperSession:
        session = DeveloperSession(
            project_root=project_root, goal=goal, status="running", meta=meta or {}
        )
        self._active[session.session_id] = session
        return session

    def get(self, session_id: str) -> DeveloperSession | None:
        return self._active.get(session_id)

    def complete(self, session: DeveloperSession, *, success: bool = True) -> None:
        session.finished_at = time.time()
        session.status = "completed" if success else "failed"
        self._active.pop(session.session_id, None)
        self._history.append(session)

    def cancel(self, session: DeveloperSession) -> None:
        session.finished_at = time.time()
        session.status = "cancelled"
        self._active.pop(session.session_id, None)
        self._history.append(session)

    def active(self) -> list[DeveloperSession]:
        return list(self._active.values())

    def recent(self, limit: int = 10) -> list[DeveloperSession]:
        sessions = list(self._history) + list(self._active.values())
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)[:limit]

    def close_all(self) -> None:
        for session in self._active.values():
            session.finished_at = time.time()
            session.status = "failed"
            self._history.append(session)
        self._active.clear()
