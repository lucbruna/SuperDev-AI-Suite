"""Central lifecycle engine coordinating all lifecycle phases."""
from __future__ import annotations

import contextlib
import time
from collections.abc import Callable
from enum import Enum, auto
from typing import Any


class AgentLifecycleState(Enum):
    CREATED = auto()
    INITIALIZING = auto()
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    SUSPENDED = auto()
    STOPPING = auto()
    STOPPED = auto()
    ERROR = auto()

    @classmethod
    def transitions(cls) -> dict[AgentLifecycleState, set[AgentLifecycleState]]:
        return {
            cls.CREATED: {cls.INITIALIZING, cls.ERROR},
            cls.INITIALIZING: {cls.READY, cls.ERROR},
            cls.READY: {cls.RUNNING, cls.STOPPING, cls.ERROR},
            cls.RUNNING: {cls.PAUSED, cls.STOPPING, cls.ERROR},
            cls.PAUSED: {cls.RUNNING, cls.SUSPENDED, cls.STOPPING},
            cls.SUSPENDED: {cls.READY, cls.STOPPING},
            cls.STOPPING: {cls.STOPPED, cls.ERROR},
            cls.STOPPED: {cls.CREATED},
            cls.ERROR: {cls.CREATED, cls.STOPPED},
        }

    def can_transition_to(self, target: AgentLifecycleState) -> bool:
        return target in self.transitions().get(self, set())


class LifecycleEvent:
    def __init__(self, agent_id: str, from_state: AgentLifecycleState,
                 to_state: AgentLifecycleState, timestamp: float,
                 metadata: dict[str, Any] | None = None) -> None:
        self.agent_id = agent_id
        self.from_state = from_state
        self.to_state = to_state
        self.timestamp = timestamp
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "from": self.from_state.name,
            "to": self.to_state.name,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class LifecycleEngine:
    """Central engine coordinating all agent lifecycle phases."""

    def __init__(self) -> None:
        self._states: dict[str, AgentLifecycleState] = {}
        self._history: dict[str, list[LifecycleEvent]] = {}
        self._hooks: dict[str, list[Callable[..., Any]]] = {}
        self._transitions_count: int = 0

    def register_agent(self, agent_id: str,
                       initial: AgentLifecycleState = AgentLifecycleState.CREATED) -> None:
        self._states[agent_id] = initial
        self._history[agent_id] = []

    def unregister_agent(self, agent_id: str) -> bool:
        if agent_id in self._states:
            del self._states[agent_id]
            self._history.pop(agent_id, None)
            return True
        return False

    def get_state(self, agent_id: str) -> AgentLifecycleState | None:
        return self._states.get(agent_id)

    def transition(self, agent_id: str, target: AgentLifecycleState,
                   metadata: dict[str, Any] | None = None) -> bool:
        current = self._states.get(agent_id)
        if current is None or not current.can_transition_to(target):
            return False
        event = LifecycleEvent(agent_id, current, target, time.time(), metadata)
        self._states[agent_id] = target
        self._history.setdefault(agent_id, []).append(event)
        self._transitions_count += 1
        self._fire_hooks(agent_id, current, target, event)
        return True

    def force_state(self, agent_id: str, state: AgentLifecycleState) -> None:
        self._states[agent_id] = state

    def add_hook(self, state_name: str, callback: Callable[..., Any]) -> None:
        self._hooks.setdefault(state_name, []).append(callback)

    def _fire_hooks(self, agent_id: str, from_s: AgentLifecycleState,
                    to_s: AgentLifecycleState, event: LifecycleEvent) -> None:
        for cb in self._hooks.get(to_s.name, []):
            with contextlib.suppress(Exception):
                cb(event)

    def get_history(self, agent_id: str, limit: int = 50) -> list[dict[str, Any]]:
        events = self._history.get(agent_id, [])
        return [e.to_dict() for e in events[-limit:]]

    def all_states(self) -> dict[str, str]:
        return {aid: st.name for aid, st in self._states.items()}

    def snapshot(self) -> dict[str, Any]:
        return {
            "agents": len(self._states),
            "transitions": self._transitions_count,
            "states": self.all_states(),
        }
