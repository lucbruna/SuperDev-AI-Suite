"""Progress tracking for long-running operations."""
from __future__ import annotations

import time
from typing import Any, Dict, Optional


class ProgressTracker:
    """Tracks progress of running operations with step-level granularity."""

    def __init__(self) -> None:
        self._operations: Dict[str, Dict[str, Any]] = {}

    def start(self, operation_id: str, total_steps: int) -> None:
        self._operations[operation_id] = {
            "operation_id": operation_id,
            "total_steps": total_steps,
            "steps_completed": 0,
            "status": "running",
            "started_at": time.time(),
            "messages": [],
        }

    def update(self, operation_id: str, steps_completed: int, message: str = "") -> None:
        if operation_id in self._operations:
            op = self._operations[operation_id]
            op["steps_completed"] = min(steps_completed, op["total_steps"])
            op["percent"] = round(op["steps_completed"] / max(op["total_steps"], 1) * 100, 1)
            if message:
                op["messages"].append({"time": time.time(), "text": message})

    def complete(self, operation_id: str) -> None:
        if operation_id in self._operations:
            op = self._operations[operation_id]
            op["status"] = "completed"
            op["completed_at"] = time.time()
            op["steps_completed"] = op["total_steps"]
            op["percent"] = 100.0

    def fail(self, operation_id: str, error: str = "") -> None:
        if operation_id in self._operations:
            op = self._operations[operation_id]
            op["status"] = "failed"
            op["error"] = error
            op["completed_at"] = time.time()

    def get_progress(self, operation_id: str) -> Optional[Dict[str, Any]]:
        op = self._operations.get(operation_id)
        if op:
            return {
                "operation_id": op["operation_id"],
                "status": op["status"],
                "steps_completed": op["steps_completed"],
                "total_steps": op["total_steps"],
                "percent": op.get("percent", 0.0),
            }
        return None

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        return {
            oid: {"status": o["status"], "percent": o.get("percent", 0.0)}
            for oid, o in self._operations.items()
        }
