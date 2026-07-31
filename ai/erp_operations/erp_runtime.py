"""ERP Runtime — Execution runtime for ERP operations."""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class ERPTaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ERPTask:
    task_id: str
    project_id: str
    name: str
    state: ERPTaskState = ERPTaskState.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ERPRuntime:
    def __init__(self):
        self.tasks: Dict[str, ERPTask] = {}
        self.handlers: Dict[str, Callable] = {}
        self.task_log: List[Dict[str, Any]] = []

    def submit_task(self, project_id: str, name: str, input_data: Optional[Dict[str, Any]] = None) -> ERPTask:
        task_id = hashlib.sha256(f"{project_id}{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        task = ERPTask(task_id=task_id, project_id=project_id, name=name, input_data=input_data or {})
        self.tasks[task_id] = task
        return task

    def execute_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False
        task.state = ERPTaskState.RUNNING
        task.started_at = datetime.now()
        handler = self.handlers.get(task.name)
        if handler:
            try:
                result = handler(task.input_data)
                task.output_data = result if isinstance(result, dict) else {"result": result}
                task.state = ERPTaskState.COMPLETED
                task.completed_at = datetime.now()
                self._log(task)
                return True
            except Exception as e:
                task.state = ERPTaskState.FAILED
                task.error = str(e)
                task.completed_at = datetime.now()
                self._log(task)
                return False
        task.state = ERPTaskState.COMPLETED
        task.completed_at = datetime.now()
        self._log(task)
        return True

    def register_handler(self, task_name: str, handler: Callable) -> None:
        self.handlers[task_name] = handler

    def get_task(self, task_id: str) -> Optional[ERPTask]:
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task and task.state == ERPTaskState.PENDING:
            task.state = ERPTaskState.CANCELLED
            return True
        return False

    def count(self) -> int:
        return len(self.tasks)

    def _log(self, task: ERPTask) -> None:
        self.task_log.append({"task_id": task.task_id, "name": task.name, "state": task.state.value, "timestamp": datetime.now().isoformat()})
