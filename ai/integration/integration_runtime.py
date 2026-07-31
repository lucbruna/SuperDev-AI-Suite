"""
Integration Runtime - Runtime execution environment
"""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import threading


class RuntimeState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class RuntimeTask:
    task_id: str
    name: str
    integration_id: str
    state: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: str = ""


class IntegrationRuntime:
    def __init__(self):
        self.state = RuntimeState.STOPPED
        self.tasks: Dict[str, RuntimeTask] = {}
        self.running_integrations: Dict[str, Dict[str, Any]] = {}
        self.logs: List[Dict[str, Any]] = []
        self.config: Dict[str, Any] = {"max_concurrent": 10, "task_timeout": 300}
        self._lock = threading.Lock()

    def start(self) -> bool:
        if self.state == RuntimeState.RUNNING:
            return False
        self.state = RuntimeState.RUNNING
        self._log("Runtime started")
        return True

    def stop(self) -> bool:
        if self.state == RuntimeState.STOPPED:
            return False
        self.state = RuntimeState.STOPPING
        self.state = RuntimeState.STOPPED
        self._log("Runtime stopped")
        return True

    def submit_task(self, name: str, integration_id: str, data: Any = None) -> RuntimeTask:
        task_id = hashlib.sha256(f"{name}{integration_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        task = RuntimeTask(task_id=task_id, name=name, integration_id=integration_id)
        self.tasks[task_id] = task
        return task

    def start_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task and task.state == "pending":
            task.state = "running"
            task.started_at = datetime.now()
            return True
        return False

    def complete_task(self, task_id: str, result: Any = None, error: str = "") -> bool:
        task = self.tasks.get(task_id)
        if task:
            task.state = "completed" if not error else "failed"
            task.completed_at = datetime.now()
            task.result = result
            task.error = error
            return True
        return False

    def register_integration(self, integration_id: str, config: Dict[str, Any] = None) -> None:
        self.running_integrations[integration_id] = config or {}

    def unregister_integration(self, integration_id: str) -> bool:
        if integration_id in self.running_integrations:
            del self.running_integrations[integration_id]
            return True
        return False

    def get_task(self, task_id: str) -> Optional[RuntimeTask]:
        return self.tasks.get(task_id)

    def get_tasks_by_integration(self, integration_id: str) -> List[RuntimeTask]:
        return [t for t in self.tasks.values() if t.integration_id == integration_id]

    def update_config(self, **kwargs) -> None:
        self.config.update(kwargs)

    def _log(self, message: str) -> None:
        self.logs.append({"message": message, "timestamp": datetime.now().isoformat(), "state": self.state.value})

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.logs[-limit:]

    def is_running(self) -> bool:
        return self.state == RuntimeState.RUNNING

    def count(self) -> int:
        return len(self.tasks)
