"""Incident response."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


class IncidentResponder:
    def __init__(self) -> None:
        self._playbooks: dict[str, list[Callable[[], Any]]] = {}
        self._executions: list[dict[str, Any]] = []
    def add_playbook(self, name: str, steps: list[Callable[[], Any]]) -> None:
        self._playbooks[name] = steps
    def execute_playbook(self, name: str, incident_id: str) -> dict[str, Any]:
        steps = self._playbooks.get(name)
        if not steps:
            return {"error": "playbook_not_found"}
        results = []
        for i, step in enumerate(steps):
            try:
                step()
                results.append({"step": i, "status": "success"})
            except Exception as e:
                results.append({"step": i, "status": "error", "error": str(e)})
        execution = {"incident_id": incident_id, "playbook": name, "results": results, "total_steps": len(steps)}
        self._executions.append(execution)
        return execution
    def list_playbooks(self) -> list[str]:
        return list(self._playbooks.keys())
    def get_executions(self, incident_id: str = "", limit: int = 50) -> list[dict[str, Any]]:
        results = self._executions
        if incident_id:
            results = [e for e in results if e["incident_id"] == incident_id]
        return results[-limit:]
    def remove_playbook(self, name: str) -> bool:
        if name in self._playbooks:
            del self._playbooks[name]
            return True
        return False
