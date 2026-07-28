from __future__ import annotations

from enum import Enum
from typing import Any

from ..base.base_agent import BaseAgent


class DebuggerEventType(Enum):
    NODE_START = "node_start"
    NODE_END = "node_end"
    NODE_ERROR = "node_error"
    BREAKPOINT_HIT = "breakpoint_hit"
    STEP_COMPLETE = "step_complete"
    VARIABLE_CHANGE = "variable_change"
    STATE_TRANSITION = "state_transition"
    FLOW_CHANGE = "flow_change"


class DebuggerEvent:
    def __init__(self, event_type: DebuggerEventType, node_id: str, data: dict[str, Any] | None = None):
        self.type = event_type
        self.node_id = node_id
        self.data = data or {}
        self.timestamp: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "node_id": self.node_id,
            "data": self.data,
            "timestamp": self.timestamp,
        }


class AgentStudioBackend:
    def __init__(self):
        self._active_sessions: dict[str, dict[str, Any]] = {}
        self._breakpoints: dict[str, list[str]] = {}
        self._step_mode: dict[str, bool] = {}
        self._event_history: dict[str, list[DebuggerEvent]] = {}
        self._inspected_vars: dict[str, set[str]] = {}

    async def create_session(self, agent_id: str) -> str:
        import uuid
        session_id = str(uuid.uuid4())
        self._active_sessions[session_id] = {
            "agent_id": agent_id,
            "status": "created",
            "current_node": None,
            "variables": {},
            "graph_state": {},
            "created_at": __import__("datetime").datetime.now().isoformat(),
        }
        self._breakpoints[session_id] = []
        self._step_mode[session_id] = False
        self._event_history[session_id] = []
        self._inspected_vars[session_id] = set()
        return session_id

    async def set_breakpoint(self, session_id: str, node_id: str) -> None:
        if session_id not in self._breakpoints:
            return
        if node_id not in self._breakpoints[session_id]:
            self._breakpoints[session_id].append(node_id)

    async def remove_breakpoint(self, session_id: str, node_id: str) -> None:
        if session_id not in self._breakpoints:
            return
        if node_id in self._breakpoints[session_id]:
            self._breakpoints[session_id].remove(node_id)

    async def list_breakpoints(self, session_id: str) -> list[str]:
        return self._breakpoints.get(session_id, [])

    async def set_step_mode(self, session_id: str, enabled: bool) -> None:
        self._step_mode[session_id] = enabled

    async def should_pause(self, session_id: str, node_id: str) -> bool:
        if session_id not in self._breakpoints:
            return False
        if node_id in self._breakpoints[session_id]:
            return True
        if self._step_mode.get(session_id, False):
            return True
        return False

    async def record_event(self, session_id: str, event: DebuggerEvent) -> None:
        import time
        event.timestamp = time.time()
        if session_id in self._event_history:
            self._event_history[session_id].append(event)
            self._active_sessions[session_id]["current_node"] = event.node_id
            self._active_sessions[session_id]["status"] = "paused" if event.type == DebuggerEventType.BREAKPOINT_HIT else "running"

    async def get_session_state(self, session_id: str) -> dict[str, Any] | None:
        return self._active_sessions.get(session_id)

    async def get_event_history(self, session_id: str) -> list[dict[str, Any]]:
        events = self._event_history.get(session_id, [])
        return [e.to_dict() for e in events]

    async def get_variables(self, session_id: str) -> dict[str, Any]:
        session = self._active_sessions.get(session_id)
        if not session:
            return {}
        return session.get("variables", {})

    async def update_variable(self, session_id: str, name: str, value: Any) -> None:
        session = self._active_sessions.get(session_id)
        if session:
            session["variables"][name] = value
            event = DebuggerEvent(DebuggerEventType.VARIABLE_CHANGE, "studio", {"name": name, "value": str(value)})
            await self.record_event(session_id, event)

    async def add_inspected_var(self, session_id: str, var_name: str) -> None:
        if session_id in self._inspected_vars:
            self._inspected_vars[session_id].add(var_name)

    async def remove_inspected_var(self, session_id: str, var_name: str) -> None:
        if session_id in self._inspected_vars:
            self._inspected_vars[session_id].discard(var_name)

    async def get_inspected_vars(self, session_id: str) -> list[str]:
        return list(self._inspected_vars.get(session_id, []))

    async def resume_session(self, session_id: str) -> None:
        session = self._active_sessions.get(session_id)
        if session:
            session["status"] = "running"

    async def stop_session(self, session_id: str) -> None:
        session = self._active_sessions.get(session_id)
        if session:
            session["status"] = "stopped"

    async def destroy_session(self, session_id: str) -> None:
        self._active_sessions.pop(session_id, None)
        self._breakpoints.pop(session_id, None)
        self._step_mode.pop(session_id, None)
        self._event_history.pop(session_id, None)
        self._inspected_vars.pop(session_id, None)

    async def list_sessions(self) -> list[dict[str, Any]]:
        result = []
        for sid, session in self._active_sessions.items():
            result.append({
                "session_id": sid,
                "agent_id": session["agent_id"],
                "status": session["status"],
                "current_node": session["current_node"],
                "created_at": session["created_at"],
                "breakpoints": self._breakpoints.get(sid, []),
                "events_count": len(self._event_history.get(sid, [])),
            })
        return result

    async def get_graph_state(self, session_id: str) -> dict[str, Any]:
        session = self._active_sessions.get(session_id)
        if not session:
            return {}
        return session.get("graph_state", {})

    async def update_graph_state(self, session_id: str, graph_state: dict[str, Any]) -> None:
        session = self._active_sessions.get(session_id)
        if session:
            session["graph_state"] = graph_state