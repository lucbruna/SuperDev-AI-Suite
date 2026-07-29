"""
Task Manager - Handles task lifecycle, scheduling, and execution tracking
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import Task, TaskStatus, TaskPriority, Event, EventType


class TaskManager:
    """Manages task lifecycle, queuing, and scheduling"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config
        self._tasks: Dict[UUID, Task] = {}
        self._queues: Dict[TaskPriority, List[Task]] = {
            TaskPriority.CRITICAL: [],
            TaskPriority.HIGH: [],
            TaskPriority.NORMAL: [],
            TaskPriority.LOW: [],
        }
        self._running_tasks: Dict[UUID, Task] = {}
        self._task_counter = 0
        self._cleanup_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def shutdown(self) -> None:
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def create_task(
        self,
        name: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        assigned_agent_id: Optional[UUID] = None,
        parent_task_id: Optional[UUID] = None,
        workflow_id: Optional[UUID] = None,
        timeout_seconds: int = 300,
        max_retries: int = 3,
    ) -> Task:
        task = Task(
            name=name,
            priority=priority,
            assigned_agent_id=assigned_agent_id,
            parent_task_id=parent_task_id,
            workflow_id=workflow_id,
            input_data=payload,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

        self._tasks[task.id] = task
        self._queues[priority].append(task)

        await self.orchestrator.publish_event(
            Event(
                type=EventType.TASK_CREATED,
                source_id=task.id,
                source_type="task",
                payload={"name": name, "priority": priority.value},
            )
        )

        return task

    def get_task(self, task_id: UUID) -> Optional[Task]:
        return self._tasks.get(task_id)

    def get_next_task(self, agent_id: UUID) -> Optional[Task]:
        for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.LOW]:
            queue = self._queues[priority]
            for i, task in enumerate(queue):
                if task.assigned_agent_id is None or task.assigned_agent_id == agent_id:
                    return queue.pop(i)
        return None

    def assign_task(self, task_id: UUID, agent_id: UUID) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.assigned_agent_id = agent_id
            return True
        return False

    def start_task(self, task_id: UUID) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            self._running_tasks[task_id] = task
            return True
        return False

    def complete_task(self, task_id: UUID, output: Dict[str, Any]) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.COMPLETED
            task.output_data = output
            task.completed_at = datetime.utcnow()
            self._running_tasks.pop(task_id, None)
            return True
        return False

    def fail_task(self, task_id: UUID, error: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.RUNNING:
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.RETRYING
                task.retry_count += 1
                task.error = error
                self._running_tasks.pop(task_id, None)
                self._queues[task.priority].insert(0, task)
            else:
                task.status = TaskStatus.FAILED
                task.error = error
                task.completed_at = datetime.utcnow()
                self._running_tasks.pop(task_id, None)
            return True
        return False

    def cancel_task(self, task_id: UUID) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status in (TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.RUNNING):
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            self._running_tasks.pop(task_id, None)

            for queue in self._queues.values():
                if task in queue:
                    queue.remove(task)
                    break

            return True
        return False

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        return [t for t in self._tasks.values() if t.status == status]

    def get_tasks_by_workflow(self, workflow_id: UUID) -> List[Task]:
        return [t for t in self._tasks.values() if t.workflow_id == workflow_id]

    def get_tasks_by_agent(self, agent_id: UUID) -> List[Task]:
        return [t for t in self._tasks.values() if t.assigned_agent_id == agent_id]

    def get_queue_stats(self) -> Dict[str, int]:
        return {
            "critical": len(self._queues[TaskPriority.CRITICAL]),
            "high": len(self._queues[TaskPriority.HIGH]),
            "normal": len(self._queues[TaskPriority.NORMAL]),
            "low": len(self._queues[TaskPriority.LOW]),
            "running": len(self._running_tasks),
            "total": len(self._tasks),
        }

    async def _cleanup_loop(self) -> None:
        while True:
            await asyncio.sleep(300)
            await self._cleanup_old_tasks()

    async def _cleanup_old_tasks(self) -> None:
        cutoff = datetime.utcnow() - timedelta(days=7)
        to_remove = [
            tid for tid, task in self._tasks.items()
            if task.completed_at and task.completed_at < cutoff
            and task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
        ]
        for tid in to_remove:
            self._tasks.pop(tid, None)