from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from .ai_types import AgentStatus


class AIState:
    """Global state management for the AI engine."""

    def __init__(self):
        self._agents: dict[str, dict[str, Any]] = {}
        self._sessions: dict[str, dict[str, Any]] = {}
        self._tasks: dict[str, dict[str, Any]] = {}
        self._global_metadata: dict[str, Any] = {}
        self._history: list[dict[str, Any]] = []

    def set_agent_state(self, agent_id: str, state: dict[str, Any]) -> None:
        """Set the state of an agent."""
        prev = self._agents.get(agent_id, {}).copy()
        self._agents[agent_id] = {**state, "updated_at": datetime.now(UTC).isoformat()}
        self._record_change("agent_state", agent_id, prev, self._agents[agent_id])

    def get_agent_state(self, agent_id: str) -> dict[str, Any] | None:
        """Get the state of an agent."""
        return self._agents.get(agent_id)

    def set_session_state(self, session_id: str, state: dict[str, Any]) -> None:
        """Set the state of a session."""
        prev = self._sessions.get(session_id, {}).copy()
        self._sessions[session_id] = {**state, "updated_at": datetime.now(UTC).isoformat()}
        self._record_change("session_state", session_id, prev, self._sessions[session_id])

    def get_session_state(self, session_id: str) -> dict[str, Any] | None:
        """Get the state of a session."""
        return self._sessions.get(session_id)

    def set_task_state(self, task_id: str, state: dict[str, Any]) -> None:
        """Set the state of a task."""
        prev = self._tasks.get(task_id, {}).copy()
        self._tasks[task_id] = {**state, "updated_at": datetime.now(UTC).isoformat()}
        self._record_change("task_state", task_id, prev, self._tasks[task_id])

    def get_task_state(self, task_id: str) -> dict[str, Any] | None:
        """Get the state of a task."""
        return self._tasks.get(task_id)

    def update_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update the status of an agent."""
        if agent_id not in self._agents:
            self._agents[agent_id] = {}
        self._agents[agent_id]["status"] = status
        self._agents[agent_id]["updated_at"] = datetime.now(UTC).isoformat()

    def set_global_metadata(self, key: str, value: Any) -> None:
        """Set a global metadata value."""
        self._global_metadata[key] = value

    def get_global_metadata(self, key: str, default: Any = None) -> Any:
        """Get a global metadata value."""
        return self._global_metadata.get(key, default)

    def reset(self) -> None:
        """Reset all state."""
        self._agents.clear()
        self._sessions.clear()
        self._tasks.clear()
        self._global_metadata.clear()

    def snapshot(self) -> dict[str, Any]:
        """Capture current state as a serializable dictionary."""
        return {
            "agents": dict(self._agents),
            "sessions": dict(self._sessions),
            "tasks": dict(self._tasks),
            "global_metadata": dict(self._global_metadata),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def to_json(self) -> str:
        """Serialize state to JSON."""
        return json.dumps(self.snapshot(), indent=2, default=str)

    def _record_change(
        self,
        change_type: str,
        entity_id: str,
        previous: dict[str, Any],
        current: dict[str, Any],
    ) -> None:
        """Record a state change in history."""
        self._history.append(
            {
                "type": change_type,
                "entity_id": entity_id,
                "previous": previous,
                "current": current,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        # Keep only last 1000 history entries
        if len(self._history) > 1000:
            self._history = self._history[-1000:]

    def get_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent state change history."""
        return self._history[-limit:]

    def health(self) -> dict[str, Any]:
        """Get state health status."""
        return {
            "status": "healthy",
            "agents": len(self._agents),
            "sessions": len(self._sessions),
            "tasks": len(self._tasks),
            "history_size": len(self._history),
            "timestamp": datetime.now(UTC).isoformat(),
        }
