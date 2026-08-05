"""Resource Monitor — CPU/memory via psutil when installed (stdlib fallback)."""
from __future__ import annotations

from typing import Any


class ResourceMonitor:
    """Reports process CPU/memory usage."""

    def collect(self) -> dict[str, Any]:
        try:
            import os
            import psutil  # type: ignore[import-not-found]

            proc = psutil.Process()
            return {
                "cpu_percent": proc.cpu_percent(interval=None),
                "memory_mb": round(proc.memory_info().rss / (1024 * 1024), 2),
                "threads": proc.num_threads(),
                "pid": os.getpid(),
                "source": "psutil",
            }
        except Exception:  # noqa: BLE001
            import os

            return {"cpu_percent": None, "memory_mb": None, "threads": None,
                    "source": "unavailable", "pid": os.getpid()}


_resource_monitor: ResourceMonitor | None = None


def get_resource_monitor() -> ResourceMonitor:
    global _resource_monitor
    if _resource_monitor is None:
        _resource_monitor = ResourceMonitor()
    return _resource_monitor
