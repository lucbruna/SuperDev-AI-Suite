from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from ..base.base_memory import BaseMemory


class WorkingMemory(BaseMemory):
    def __init__(self) -> None:
        self._goals: list[dict[str, Any]] = []
        self._sub_tasks: list[dict[str, Any]] = []
        self._results: list[dict[str, Any]] = []
        self._context: dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._session_id: str = str(uuid.uuid4())

    async def store(self, key: str, value: Any) -> None:
        async with self._lock:
            self._context[key] = value

    async def retrieve(self, key: str) -> Any | None:
        async with self._lock:
            return self._context.get(key)

    async def search(self, query: str) -> list[Any]:
        results = []
        q = query.lower()
        async with self._lock:
            for key, value in self._context.items():
                if q in key.lower():
                    results.append(value)
        return results

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._context.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._goals.clear()
            self._sub_tasks.clear()
            self._results.clear()
            self._context.clear()

    async def add_goal(self, goal: str, priority: int = 0) -> str:
        goal_id = str(uuid.uuid4())
        async with self._lock:
            self._goals.append({
                "id": goal_id,
                "goal": goal,
                "priority": priority,
                "status": "active",
                "created_at": time.time(),
            })
        return goal_id

    async def add_sub_task(self, task: str, depends_on: list[str] | None = None) -> str:
        task_id = str(uuid.uuid4())
        async with self._lock:
            self._sub_tasks.append({
                "id": task_id,
                "task": task,
                "depends_on": depends_on or [],
                "status": "pending",
                "created_at": time.time(),
            })
        return task_id

    async def add_result(self, result: dict[str, Any]) -> None:
        async with self._lock:
            self._results.append({
                **result,
                "timestamp": time.time(),
            })

    def get_session_id(self) -> str:
        return self._session_id
