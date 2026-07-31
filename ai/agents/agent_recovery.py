from __future__ import annotations

from typing import Any

from .agent_checkpoint import AgentCheckpoint
from .agent_snapshot import AgentSnapshot


class AgentRecovery:
    """Recovery mechanisms for failed agents."""

    def __init__(self) -> None:
        self._checkpoint = AgentCheckpoint()
        self._snapshot = AgentSnapshot()
        self._recovery_count: int = 0

    @property
    def recovery_count(self) -> int:
        return self._recovery_count

    @property
    def checkpoint(self) -> AgentCheckpoint:
        return self._checkpoint

    @property
    def snapshot(self) -> AgentSnapshot:
        return self._snapshot

    def recover_from_checkpoint(self, agent_id: str) -> dict[str, Any] | None:
        state = self._checkpoint.load(agent_id)
        if state is not None:
            self._recovery_count += 1
        return state

    def recover_from_snapshot(self, agent_id: str) -> dict[str, Any] | None:
        state = self._snapshot.restore(agent_id)
        if state is not None:
            self._recovery_count += 1
        return state

    def reset(self) -> None:
        self._recovery_count = 0
