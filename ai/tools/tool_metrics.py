from __future__ import annotations

import time
from typing import Any


class ToolMetrics:
    """Collects metrics about tool usage and performance."""

    def __init__(self) -> None:
        self._execution_times: dict[str, list[float]] = {}
        self._call_counts: dict[str, int] = {}
        self._error_counts: dict[str, int] = {}
        self._start_time: float = time.time()

    def record_execution(self, tool_name: str, duration: float) -> None:
        if tool_name not in self._execution_times:
            self._execution_times[tool_name] = []
        self._execution_times[tool_name].append(duration)
        self._call_counts[tool_name] = self._call_counts.get(tool_name, 0) + 1

    def record_error(self, tool_name: str) -> None:
        self._error_counts[tool_name] = self._error_counts.get(tool_name, 0) + 1

    def get_call_count(self, tool_name: str) -> int:
        return self._call_counts.get(tool_name, 0)

    def get_error_count(self, tool_name: str) -> int:
        return self._error_counts.get(tool_name, 0)

    def get_avg_execution_time(self, tool_name: str) -> float:
        times = self._execution_times.get(tool_name, [])
        if not times:
            return 0.0
        return sum(times) / len(times)

    def get_total_calls(self) -> int:
        return sum(self._call_counts.values())

    def get_total_errors(self) -> int:
        return sum(self._error_counts.values())

    def get_uptime(self) -> float:
        return time.time() - self._start_time

    @property
    def tool_names(self) -> list[str]:
        return list(self._call_counts.keys())

    @property
    def tool_count(self) -> int:
        return len(self._call_counts)

    def summary(self, tool_name: str) -> dict[str, Any]:
        return {
            "calls": self.get_call_count(tool_name),
            "errors": self.get_error_count(tool_name),
            "avg_time": self.get_avg_execution_time(tool_name),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_calls": self.get_total_calls(),
            "total_errors": self.get_total_errors(),
            "tools": {t: self.summary(t) for t in self._call_counts},
            "uptime": self.get_uptime(),
        }
