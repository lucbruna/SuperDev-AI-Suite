from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict, Optional


class AgentState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()
    ERROR = auto()


class AgentStateManager:
    """Manages agent state transitions."""

    def __init__(self, initial: AgentState = AgentState.IDLE) -> None:
        self._state = initial

    @property
    def state(self) -> AgentState:
        return self._state

    def transition_to(self, new_state: AgentState) -> bool:
        allowed = self._allowed_transitions(self._state)
        if new_state in allowed:
            self._state = new_state
            return True
        return False

    def is_idle(self) -> bool:
        return self._state == AgentState.IDLE

    def is_running(self) -> bool:
        return self._state == AgentState.RUNNING

    def is_stopped(self) -> bool:
        return self._state == AgentState.STOPPED

    def _allowed_transitions(self, current: AgentState) -> set:
        transitions = {
            AgentState.IDLE: {AgentState.RUNNING, AgentState.STOPPED},
            AgentState.RUNNING: {AgentState.PAUSED, AgentState.STOPPED, AgentState.ERROR},
            AgentState.PAUSED: {AgentState.RUNNING, AgentState.STOPPED},
            AgentState.STOPPED: {AgentState.IDLE},
            AgentState.ERROR: {AgentState.IDLE, AgentState.STOPPED},
        }
        return transitions.get(current, set())

    def to_dict(self) -> Dict[str, Any]:
        return {"state": self._state.name}
