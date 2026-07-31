from __future__ import annotations

from typing import Any


class LeaderElection:
    """Elects a leader among agents."""

    def __init__(self) -> None:
        self._leader: str | None = None
        self._candidates: list[str] = []
        self._election_count: int = 0

    @property
    def leader(self) -> str | None:
        return self._leader

    @property
    def election_count(self) -> int:
        return self._election_count

    def nominate(self, agent_id: str) -> None:
        if agent_id not in self._candidates:
            self._candidates.append(agent_id)

    def elect(self) -> str | None:
        if not self._candidates:
            return None
        self._leader = self._candidates[0]
        self._election_count += 1
        self._candidates.clear()
        return self._leader

    def step_down(self) -> None:
        self._leader = None

    def clear(self) -> None:
        self._leader = None
        self._candidates.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "leader": self._leader,
            "election_count": self._election_count,
        }
