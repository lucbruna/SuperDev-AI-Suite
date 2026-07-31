"""Process simulator."""

from __future__ import annotations

from typing import Any


class ProcessSimulator:
    def __init__(self) -> None:
        self._processes: dict[str, dict[str, Any]] = {}
        self._results: list[dict[str, Any]] = []

    def define(self, process_id: str, name: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
        process = {"process_id": process_id, "name": name, "steps": steps, "current_step": 0}
        self._processes[process_id] = process
        return process

    def execute_step(self, process_id: str, context: dict[str, Any] = None) -> dict[str, Any]:
        if process_id not in self._processes:
            return {"error": "not_found"}
        process = self._processes[process_id]
        if process["current_step"] >= len(process["steps"]):
            return {"status": "completed", "process_id": process_id}
        step = process["steps"][process["current_step"]]
        process["current_step"] += 1
        result = {"process_id": process_id, "step": step.get("name", ""), "status": "executed"}
        self._results.append(result)
        return result

    def execute_all(self, process_id: str, context: dict[str, Any] = None) -> dict[str, Any]:
        results = []
        while True:
            r = self.execute_step(process_id, context)
            if r.get("status") == "completed" or "error" in r:
                break
            results.append(r)
        return {"process_id": process_id, "results": results, "total": len(results)}

    def get_process(self, process_id: str) -> dict[str, Any]:
        return self._processes.get(process_id, {"error": "not_found"})

    def list_processes(self) -> list[dict[str, Any]]:
        return list(self._processes.values())

    def get_results(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._results[-limit:]

    def count(self) -> int:
        return len(self._processes)
