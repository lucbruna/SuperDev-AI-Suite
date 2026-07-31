"""Improvement tracking for agents (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_protocols import new_id, now


class ImprovementTracker:
    """Records improvement proposals and whether they were applied."""

    def __init__(self) -> None:
        self._improvements: list[dict[str, Any]] = []

    def record(self, agent_id: str, description: str,
               kind: str = "general") -> dict[str, Any]:
        entry = {"improvement_id": new_id("improve"), "agent_id": agent_id,
                 "description": description, "kind": kind,
                 "applied": False, "created_at": now()}
        self._improvements.append(entry)
        return entry

    def list(self, agent_id: str | None = None) -> list[dict[str, Any]]:
        if agent_id is None:
            return list(self._improvements)
        return [entry for entry in self._improvements
                if entry["agent_id"] == agent_id]

    def mark_applied(self, improvement_id: str) -> bool:
        for entry in self._improvements:
            if entry["improvement_id"] == improvement_id:
                entry["applied"] = True
                return True
        return False

    def applied_count(self) -> int:
        return sum(1 for entry in self._improvements if entry["applied"])

    def count(self) -> int:
        return len(self._improvements)
