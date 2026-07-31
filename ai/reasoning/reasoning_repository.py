from __future__ import annotations

from .reasoning_models import ReasoningResult


class ReasoningRepository:
    """Persistence layer for reasoning results and sessions."""

    def __init__(self):
        self._store: dict[str, ReasoningResult] = {}
        self._sessions: dict[str, list[ReasoningResult]] = {}

    def save_result(self, result: ReasoningResult) -> None:
        self._store[result.context_id] = result

    def get_result(self, context_id: str) -> ReasoningResult | None:
        return self._store.get(context_id)

    def save_session_result(self, session_id: str, result: ReasoningResult) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(result)

    def get_session_results(self, session_id: str) -> list[ReasoningResult]:
        return self._sessions.get(session_id, [])

    def list_all(self) -> list[ReasoningResult]:
        return list(self._store.values())

    def delete_result(self, context_id: str) -> bool:
        return self._store.pop(context_id, None) is not None
