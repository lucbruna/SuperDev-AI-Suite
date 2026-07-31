"""Incident response."""
from __future__ import annotations
from typing import Any, Callable, Dict, List

class IncidentResponder:
    def __init__(self) -> None:
        self._playbooks: Dict[str, List[Callable[[], Any]]] = {}
        self._executions: List[Dict[str, Any]] = []
    def add_playbook(self, name: str, steps: List[Callable[[], Any]]) -> None:
        self._playbooks[name] = steps
    def execute_playbook(self, name: str, incident_id: str) -> Dict[str, Any]:
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
    def list_playbooks(self) -> List[str]:
        return list(self._playbooks.keys())
    def get_executions(self, incident_id: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        results = self._executions
        if incident_id:
            results = [e for e in results if e["incident_id"] == incident_id]
        return results[-limit:]
    def remove_playbook(self, name: str) -> bool:
        if name in self._playbooks:
            del self._playbooks[name]
            return True
        return False
