"""Feedback collection for agents (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_protocols import now


class FeedbackCollector:
    """Collects human/system feedback notes per agent."""

    def __init__(self) -> None:
        self._feedback: dict[str, list[dict]] = {}

    def add(self, agent_id: str, text: str,
            source: str = "human") -> dict:
        entry = {"text": text, "source": source, "created_at": now()}
        self._feedback.setdefault(agent_id, []).append(entry)
        return entry

    def list(self, agent_id: str | None = None) -> list[dict]:
        if agent_id is None:
            return [entry for entries in self._feedback.values()
                    for entry in entries]
        return list(self._feedback.get(agent_id, []))

    def latest(self, agent_id: str) -> str:
        entries = self._feedback.get(agent_id, [])
        return entries[-1]["text"] if entries else ""

    def count(self, agent_id: str | None = None) -> int:
        if agent_id is None:
            return sum(len(entries) for entries in self._feedback.values())
        return len(self._feedback.get(agent_id, []))
