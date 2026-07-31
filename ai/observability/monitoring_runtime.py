"""Monitoring runtime management."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class MonitoringRuntime:
    def __init__(self) -> None:
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._history: List[Dict[str, Any]] = []
        self._running = False
    def start(self) -> None:
        self._running = True
    def stop(self) -> None:
        self._running = False
    def is_running(self) -> bool:
        return self._running
    def register_task(self, task_id: str, name: str, interval: int = 60) -> Dict[str, Any]:
        task = {"task_id": task_id, "name": name, "interval": interval, "last_run": 0, "run_count": 0, "active": True}
        self._tasks[task_id] = task
        return task
    def run_task(self, task_id: str) -> Dict[str, Any]:
        task = self._tasks.get(task_id)
        if not task:
            return {"error": "task_not_found"}
        task["last_run"] = time.time()
        task["run_count"] += 1
        entry = {"task_id": task_id, "timestamp": time.time(), "status": "completed"}
        self._history.append(entry)
        return entry
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)
    def list_tasks(self) -> List[Dict[str, Any]]:
        return list(self._tasks.values())
    def get_history(self, task_id: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        history = self._history
        if task_id:
            history = [h for h in history if h["task_id"] == task_id]
        return history[-limit:]
