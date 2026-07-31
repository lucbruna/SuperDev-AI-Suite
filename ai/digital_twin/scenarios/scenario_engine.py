"""Scenario engine."""

from __future__ import annotations

import time
from typing import Any


class ScenarioEngine:
    def __init__(self) -> None:
        self._scenarios: dict[str, dict[str, Any]] = {}
        self._started = False

    def start(self) -> None:
        self._started = True

    def create(
        self, scenario_id: str, name: str, description: str = "", parameters: dict[str, Any] = None
    ) -> dict[str, Any]:
        scenario = {
            "scenario_id": scenario_id,
            "name": name,
            "description": description,
            "parameters": parameters or {},
            "state": "draft",
            "results": [],
            "created_at": time.time(),
        }
        self._scenarios[scenario_id] = scenario
        return scenario

    def get(self, scenario_id: str) -> dict[str, Any]:
        return self._scenarios.get(scenario_id, {"error": "not_found"})

    def update(self, scenario_id: str, **kwargs: Any) -> bool:
        if scenario_id not in self._scenarios:
            return False
        self._scenarios[scenario_id].update(kwargs)
        return True

    def delete(self, scenario_id: str) -> bool:
        if scenario_id in self._scenarios:
            del self._scenarios[scenario_id]
            return True
        return False

    def add_result(self, scenario_id: str, result: dict[str, Any]) -> bool:
        if scenario_id not in self._scenarios:
            return False
        self._scenarios[scenario_id]["results"].append(result)
        return True

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._scenarios.values())

    def list_by_state(self, state: str) -> list[dict[str, Any]]:
        return [s for s in self._scenarios.values() if s.get("state") == state]

    def count(self) -> int:
        return len(self._scenarios)

    def is_running(self) -> bool:
        return self._started
