"""Simulation engine."""
from __future__ import annotations

import time
from typing import Any


class SimulationEngine:
    def __init__(self) -> None:
        self._simulations: dict[str, dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def create(self, sim_id: str, name: str, config: dict[str, Any] = None) -> dict[str, Any]:
        sim = {"sim_id": sim_id, "name": name, "config": config or {"time_steps": 100, "dt": 1.0}, "state": "idle", "results": [], "created_at": time.time()}
        self._simulations[sim_id] = sim
        return sim
    def run(self, sim_id: str, steps: int = None) -> dict[str, Any]:
        if sim_id not in self._simulations:
            return {"error": "not_found"}
        sim = self._simulations[sim_id]
        sim["state"] = "running"
        num_steps = steps or sim["config"].get("time_steps", 100)
        events = []
        for i in range(num_steps):
            events.append({"step": i, "time": i * sim["config"].get("dt", 1.0)})
        sim["state"] = "completed"
        sim["results"] = events
        return {"sim_id": sim_id, "steps": num_steps, "events": len(events)}
    def pause(self, sim_id: str) -> bool:
        if sim_id in self._simulations:
            self._simulations[sim_id]["state"] = "paused"
            return True
        return False
    def resume(self, sim_id: str) -> bool:
        if sim_id in self._simulations:
            self._simulations[sim_id]["state"] = "running"
            return True
        return False
    def get(self, sim_id: str) -> dict[str, Any]:
        return self._simulations.get(sim_id, {"error": "not_found"})
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._simulations.values())
    def count(self) -> int:
        return len(self._simulations)
    def is_running(self) -> bool:
        return self._started
