from __future__ import annotations

from typing import Any


class AsyncOptimizer:
    """Analyzes tasks and recommends async optimizations."""

    IO_KEYWORDS = ["io", "network", "database", "file", "http", "api", "request", "disk"]

    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}

    def analyze_task(self, task_desc: str) -> list[dict[str, Any]]:
        desc_lower = task_desc.lower()
        results = []
        for keyword in self.IO_KEYWORDS:
            if keyword in desc_lower:
                results.append(
                    {
                        "task": task_desc[:50],
                        "pattern": f"{keyword}_bound",
                        "recommendation": f"Use asyncio for {keyword} operations",
                        "estimated_speedup": "3-10x",
                    }
                )
        if not results:
            results.append(
                {
                    "task": task_desc[:50],
                    "pattern": "cpu_bound",
                    "recommendation": "Use multiprocessing for CPU-bound tasks",
                    "estimated_speedup": "1-2x",
                }
            )
        return results

    def add_task(self, name: str, duration_ms: float, is_io_bound: bool) -> str:
        self._tasks[name] = {
            "name": name,
            "duration_ms": duration_ms,
            "is_io_bound": is_io_bound,
            "async_eligible": is_io_bound,
        }
        return name

    def get_task(self, name: str) -> dict[str, Any] | None:
        return self._tasks.get(name)

    def list_tasks(self) -> list[dict[str, Any]]:
        return list(self._tasks.values())

    @property
    def task_count(self) -> int:
        return len(self._tasks)

    def estimate_speedup(self, task_names: list[str] | None = None) -> float:
        tasks = [t for n, t in self._tasks.items() if task_names is None or n in task_names]
        if not tasks:
            return 1.0
        io_tasks = sum(1 for t in tasks if t["is_io_bound"])
        if io_tasks == 0:
            return 1.0
        ratio = io_tasks / len(tasks)
        return round(1.0 + ratio * 2.0, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tasks": list(self._tasks.values()),
            "task_count": self.task_count,
        }
