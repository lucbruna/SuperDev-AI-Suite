from __future__ import annotations

from typing import Any


class DesignDecision:
    """ADR-style design decision records with context, options, and consequences."""

    def __init__(self) -> None:
        self._decisions: dict[str, dict[str, Any]] = {}

    def record(
        self,
        decision_id: str,
        title: str,
        context: str,
        options: list[str],
        decision: str,
        consequences: list[str],
    ) -> str:
        entry = {
            "id": decision_id,
            "title": title,
            "context": context,
            "options": options,
            "decision": decision,
            "consequences": consequences,
            "status": "accepted",
        }
        self._decisions[decision_id] = entry
        return decision_id

    def get(self, decision_id: str) -> dict[str, Any] | None:
        return self._decisions.get(decision_id)

    def list_decisions(self) -> list[dict[str, Any]]:
        return list(self._decisions.values())

    @property
    def decision_count(self) -> int:
        return len(self._decisions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decisions": self._decisions,
            "decision_count": self.decision_count,
        }
