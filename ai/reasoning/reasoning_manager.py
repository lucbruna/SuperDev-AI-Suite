from __future__ import annotations

from typing import Any

from .reasoning_context import ReasoningContext
from .reasoning_engine import ReasoningEngine
from .reasoning_models import ReasoningResult


class ReasoningManager:
    """Manages reasoning lifecycle and coordinates sub-components."""

    def __init__(self, engine: ReasoningEngine | None = None):
        self._engine = engine or ReasoningEngine()
        self._active_sessions: dict[str, ReasoningContext] = {}

    async def start_session(self, context: ReasoningContext) -> str:
        session_id = context.context_id
        self._active_sessions[session_id] = context
        return session_id

    async def run(self, context: ReasoningContext) -> ReasoningResult:
        return await self._engine.reason(context)

    async def close_session(self, session_id: str) -> None:
        self._active_sessions.pop(session_id, None)

    def list_sessions(self) -> list[str]:
        return list(self._active_sessions.keys())

    def status(self) -> dict[str, Any]:
        return {"active_sessions": len(self._active_sessions)}
