"""Scenario manager."""
from __future__ import annotations
from typing import Any, Dict, List

class ScenarioManager:
    def __init__(self) -> None:
        self._scenarios: Dict[str, Dict[str, Any]] = {}
        self._groups: Dict[str, List[str]] = {}
    def add(self, scenario_id: str, name: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        scenario = {"scenario_id": scenario_id, "name": name, "config": config or {}, "status": "active"}
        self._scenarios[scenario_id] = scenario
        return scenario
    def get(self, scenario_id: str) -> Dict[str, Any]:
        return self._scenarios.get(scenario_id, {"error": "not_found"})
    def archive(self, scenario_id: str) -> bool:
        if scenario_id in self._scenarios:
            self._scenarios[scenario_id]["status"] = "archived"
            return True
        return False
    def group(self, group_name: str, scenario_ids: List[str]) -> Dict[str, Any]:
        self._groups[group_name] = scenario_ids
        return {"group": group_name, "scenarios": scenario_ids}
    def get_group(self, group_name: str) -> List[Dict[str, Any]]:
        ids = self._groups.get(group_name, [])
        return [self._scenarios[sid] for sid in ids if sid in self._scenarios]
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._scenarios.values())
    def list_active(self) -> List[Dict[str, Any]]:
        return [s for s in self._scenarios.values() if s["status"] == "active"]
    def delete(self, scenario_id: str) -> bool:
        if scenario_id in self._scenarios:
            del self._scenarios[scenario_id]
            return True
        return False
    def count(self) -> int:
        return len(self._scenarios)
