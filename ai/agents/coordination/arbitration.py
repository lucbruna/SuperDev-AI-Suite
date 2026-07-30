from __future__ import annotations

from typing import Any, Dict, Optional


class Arbitration:
    """Resolves conflicts between agents."""

    def __init__(self) -> None:
        self._conflicts: Dict[str, Dict[str, Any]] = {}
        self._resolved: int = 0

    @property
    def resolved_count(self) -> int:
        return self._resolved

    def register_conflict(self, conflict_id: str, agent_a: str, agent_b: str, issue: str) -> None:
        self._conflicts[conflict_id] = {
            "agents": (agent_a, agent_b),
            "issue": issue,
            "resolution": None,
        }

    def resolve(self, conflict_id: str, decision: str) -> bool:
        conflict = self._conflicts.get(conflict_id)
        if conflict:
            conflict["resolution"] = decision
            self._resolved += 1
            return True
        return False

    def get_conflict(self, conflict_id: str) -> Optional[Dict[str, Any]]:
        conflict = self._conflicts.get(conflict_id)
        return dict(conflict) if conflict else None

    def clear(self) -> None:
        self._conflicts.clear()
        self._resolved = 0
