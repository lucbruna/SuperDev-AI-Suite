"""System dashboard."""

from __future__ import annotations

from typing import Any


class SystemDashboard:
    def __init__(self) -> None:
        self._metrics: dict[str, Any] = {}

    def update_metrics(self, metrics: dict[str, Any]) -> None:
        self._metrics.update(metrics)

    def get_cpu_usage(self) -> float:
        return self._metrics.get("cpu_usage", 0.0)

    def get_memory_usage(self) -> float:
        return self._metrics.get("memory_usage", 0.0)

    def get_disk_usage(self) -> float:
        return self._metrics.get("disk_usage", 0.0)

    def get_network_io(self) -> dict[str, float]:
        return {"bytes_in": self._metrics.get("net_in", 0), "bytes_out": self._metrics.get("net_out", 0)}

    def get_process_count(self) -> int:
        return int(self._metrics.get("process_count", 0))

    def get_uptime(self) -> float:
        return self._metrics.get("uptime", 0.0)

    def get_summary(self) -> dict[str, Any]:
        return {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "processes": self.get_process_count(),
        }
