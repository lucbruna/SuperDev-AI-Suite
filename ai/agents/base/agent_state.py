from __future__ import annotations

from enum import Enum, auto
from typing import Any


class AgentState(Enum):
    CREATED = auto()
    INITIALIZING = auto()
    IDLE = auto()
    BUSY = auto()
    PAUSED = auto()
    ERROR = auto()
    STOPPED = auto()


class AgentStateManager:
    """Manages agent state transitions."""

    def __init__(self, initial: AgentState = AgentState.CREATED) -> None:
        self._state = initial

    @property
    def state(self) -> AgentState:
        return self._state

    def transition(self, new: AgentState) -> bool:
        allowed = {
            AgentState.CREATED: {AgentState.INITIALIZING},
            AgentState.INITIALIZING: {AgentState.IDLE, AgentState.ERROR},
            AgentState.IDLE: {AgentState.BUSY, AgentState.STOPPED},
            AgentState.BUSY: {AgentState.IDLE, AgentState.PAUSED, AgentState.ERROR},
            AgentState.PAUSED: {AgentState.BUSY, AgentState.IDLE, AgentState.STOPPED},
            AgentState.ERROR: {AgentState.IDLE, AgentState.STOPPED},
            AgentState.STOPPED: set(),
        }
        if new in allowed.get(self._state, set()):
            self._state = new
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {"state": self._state.name}
