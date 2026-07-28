from __future__ import annotations

from typing import Any


class AgentInspector:
    def __init__(self):
        self._snapshots: dict[str, list[dict[str, Any]]] = {}
        self._watch_expressions: dict[str, list[str]] = {}

    async def snapshot_state(self, session_id: str, agent: Any, node_id: str) -> dict[str, Any]:
        snapshot = {
            "node_id": node_id,
            "agent_name": getattr(agent, "name", str(agent.__class__.__name__)),
            "agent_state": self._extract_agent_state(agent),
            "variables": self._extract_variables(agent),
            "memory": await self._extract_memory(agent),
            "stack": self._extract_stack(agent),
            "timestamp": __import__("time").time(),
        }
        if session_id not in self._snapshots:
            self._snapshots[session_id] = []
        self._snapshots[session_id].append(snapshot)
        return snapshot

    def _extract_agent_state(self, agent: Any) -> dict[str, Any]:
        state = {}
        for attr in ["status", "state", "phase", "mode", "configuration", "config"]:
            value = getattr(agent, attr, None)
            if value is not None:
                state[attr] = str(value) if not isinstance(value, (dict, list, str, int, float, bool)) else value
        return state

    def _extract_variables(self, agent: Any) -> dict[str, Any]:
        variables = {}
        for attr in dir(agent):
            if attr.startswith("_") or attr.startswith("__"):
                continue
            value = getattr(agent, attr, None)
            if callable(value):
                continue
            try:
                str_value = str(value)
                if len(str_value) < 500:
                    variables[attr] = str_value
            except Exception:
                variables[attr] = "<unserializable>"
        return variables

    async def _extract_memory(self, agent: Any) -> dict[str, Any]:
        memory = getattr(agent, "memory", None)
        if memory is None:
            return {}
        try:
            if hasattr(memory, "get_all") and callable(memory.get_all):
                return await memory.get_all()
            if hasattr(memory, "_data"):
                data = memory._data
                if callable(data):
                    return {}
                return dict(data) if isinstance(data, dict) else {"raw": str(data)[:500]}
        except Exception:
            return {"error": "Could not extract memory"}
        return {}

    def _extract_stack(self, agent: Any) -> list[dict[str, str]]:
        stack = []
        execution_context = getattr(agent, "_execution_context", None) or getattr(agent, "context", None)
        if execution_context:
            stack.append({"frame": "execution_context", "value": str(execution_context)[:300]})
        current_task = getattr(agent, "_current_task", None) or getattr(agent, "task", None)
        if current_task:
            stack.append({"frame": "current_task", "value": str(current_task)[:300]})
        return stack

    async def get_snapshots(self, session_id: str) -> list[dict[str, Any]]:
        return self._snapshots.get(session_id, [])

    async def get_latest_snapshot(self, session_id: str) -> dict[str, Any] | None:
        snapshots = self._snapshots.get(session_id, [])
        return snapshots[-1] if snapshots else None

    async def clear_snapshots(self, session_id: str) -> None:
        self._snapshots.pop(session_id, None)

    async def add_watch_expression(self, session_id: str, expression: str) -> None:
        if session_id not in self._watch_expressions:
            self._watch_expressions[session_id] = []
        if expression not in self._watch_expressions[session_id]:
            self._watch_expressions[session_id].append(expression)

    async def remove_watch_expression(self, session_id: str, expression: str) -> None:
        if session_id in self._watch_expressions:
            if expression in self._watch_expressions[session_id]:
                self._watch_expressions[session_id].remove(expression)

    async def get_watch_expressions(self, session_id: str) -> list[str]:
        return self._watch_expressions.get(session_id, [])

    async def evaluate_watch(self, expression: str, variables: dict[str, Any]) -> str:
        try:
            local_vars = dict(variables)
            result = eval(expression, {"__builtins__": {}}, local_vars)
            return str(result)
        except Exception as e:
            return f"<error: {e}>"

    async def diff_snapshots(self, session_id: str, snap1_idx: int = -2, snap2_idx: int = -1) -> dict[str, Any]:
        snapshots = self._snapshots.get(session_id, [])
        if len(snapshots) < 2:
            return {}
        s1 = snapshots[snap1_idx]
        s2 = snapshots[snap2_idx]
        changes: dict[str, Any] = {"variables_changed": {}, "state_changed": {}}
        v1 = s1.get("variables", {})
        v2 = s2.get("variables", {})
        for key in set(list(v1.keys()) + list(v2.keys())):
            if v1.get(key) != v2.get(key):
                changes["variables_changed"][key] = {"from": v1.get(key), "to": v2.get(key)}
        s1_state = s1.get("agent_state", {})
        s2_state = s2.get("agent_state", {})
        for key in set(list(s1_state.keys()) + list(s2_state.keys())):
            if s1_state.get(key) != s2_state.get(key):
                changes["state_changed"][key] = {"from": s1_state.get(key), "to": s2_state.get(key)}
        return changes