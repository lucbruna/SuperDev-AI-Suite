"""Recovery engine."""
from __future__ import annotations

import time
from typing import Any


class RecoveryEngine:
    def __init__(self) -> None:
        self._plans: dict[str, dict[str, Any]] = {}
        self._incidents: list[dict[str, Any]] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def create_plan(self, name: str, description: str = "", steps: list[str] = None) -> dict[str, Any]:
        plan = {"name": name, "description": description, "steps": steps or ["detect", "failover", "recover", "verify"], "status": "active"}
        self._plans[name] = plan
        return plan
    def get_plan(self, name: str) -> dict[str, Any]:
        return self._plans.get(name, {"error": "not_found"})
    def execute_plan(self, name: str, incident: str = "") -> dict[str, Any]:
        if name not in self._plans:
            return {"error": "not_found"}
        plan = self._plans[name]
        results = [{"step": step, "status": "completed"} for step in plan["steps"]]
        incident_entry = {"plan": name, "incident": incident, "results": results, "status": "recovered", "timestamp": time.time()}
        self._incidents.append(incident_entry)
        return incident_entry
    def list_plans(self) -> list[dict[str, Any]]:
        return list(self._plans.values())
    def list_incidents(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._incidents[-limit:]
    def count(self) -> int:
        return len(self._plans)
    def is_running(self) -> bool:
        return self._started
