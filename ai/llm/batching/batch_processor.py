from __future__ import annotations

import time
import uuid
from typing import Any

from ..llm_executor import LLMExecutor


class BatchProcessor:
    """Processes multiple LLM requests in batches."""

    def __init__(self, executor: LLMExecutor | None = None) -> None:
        self._executor = executor
        self._queue: list[dict[str, Any]] = []
        self._completed: list[dict[str, Any]] = []
        self._failed: list[dict[str, Any]] = []

    def set_executor(self, executor: LLMExecutor) -> None:
        self._executor = executor

    def add_task(self, provider: str, prompt: str, **kwargs: Any) -> str:
        task_id = str(uuid.uuid4())[:8]
        self._queue.append({
            "task_id": task_id,
            "provider": provider,
            "prompt": prompt,
            "params": kwargs,
            "added_at": time.time(),
        })
        return task_id

    async def process_all(self, batch_size: int = 10) -> list[dict[str, Any]]:
        if self._executor is None:
            raise RuntimeError("No executor configured")

        results: list[dict[str, Any]] = []
        while self._queue:
            batch = self._queue[:batch_size]
            self._queue = self._queue[batch_size:]

            for task in batch:
                try:
                    result = await self._executor.execute(
                        task["provider"], task["prompt"], **task["params"]
                    )
                    result["task_id"] = task["task_id"]
                    if result.get("success", False):
                        self._completed.append(result)
                    else:
                        self._failed.append(result)
                    results.append(result)
                except Exception as e:
                    error = {"task_id": task["task_id"], "success": False, "error": str(e)}
                    self._failed.append(error)
                    results.append(error)

        return results

    async def process_batch(self, tasks: list[tuple[str, str, dict[str, Any]]]) -> list[dict[str, Any]]:
        if self._executor is None:
            raise RuntimeError("No executor configured")

        results: list[dict[str, Any]] = []
        for provider, prompt, params in tasks:
            try:
                result = await self._executor.execute(provider, prompt, **params)
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e)})
        return results

    def get_status(self) -> dict[str, Any]:
        return {
            "queued": len(self._queue),
            "completed": len(self._completed),
            "failed": len(self._failed),
            "total": len(self._queue) + len(self._completed) + len(self._failed),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.get_status(),
            "has_executor": self._executor is not None,
        }
