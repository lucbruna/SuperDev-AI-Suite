"""Scenario runner."""
from __future__ import annotations
from typing import Any, Dict, List

class ScenarioRunner:
    def __init__(self) -> None:
        self._scenarios: Dict[str, Dict[str, Any]] = {}
        self._results: List[Dict[str, Any]] = []
    def add_scenario(self, scenario_id: str, name: str, parameters: Dict[str, Any], simulation_fn=None) -> Dict[str, Any]:
        scenario = {"scenario_id": scenario_id, "name": name, "parameters": parameters, "simulation_fn": simulation_fn}
        self._scenarios[scenario_id] = scenario
        return {"scenario_id": scenario_id, "name": name}
    def run(self, scenario_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        if scenario_id not in self._scenarios:
            return {"error": "not_found"}
        scenario = self._scenarios[scenario_id]
        fn = scenario.get("simulation_fn")
        if fn:
            result = fn(scenario["parameters"], context or {})
        else:
            result = {"scenario": scenario["name"], "status": "simulated", "metrics": {"score": 0.8}}
        self._results.append({"scenario_id": scenario_id, "result": result})
        return result
    def run_all(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        results = {}
        for sid in self._scenarios:
            results[sid] = self.run(sid, context)
        return results
    def compare(self, scenario_ids: List[str]) -> Dict[str, Any]:
        comparison = {}
        for r in self._results:
            if r["scenario_id"] in scenario_ids:
                comparison[r["scenario_id"]] = r["result"]
        return comparison
    def get_results(self, scenario_id: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        results = self._results
        if scenario_id:
            results = [r for r in results if r["scenario_id"] == scenario_id]
        return results[-limit:]
    def list_scenarios(self) -> List[str]:
        return list(self._scenarios.keys())
    def count(self) -> int:
        return len(self._scenarios)
