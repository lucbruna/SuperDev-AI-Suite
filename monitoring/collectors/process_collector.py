from __future__ import annotations

import os
import time
from typing import Any


class ProcessCollector:
    """Collects process-level metrics."""

    def collect(self) -> dict[str, Any]:
        import psutil
        proc = psutil.Process()
        with proc.oneshot():
            return {
                "pid": proc.pid,
                "name": proc.name(),
                "cpu_percent": proc.cpu_percent(interval=0),
                "memory_rss": proc.memory_info().rss,
                "memory_percent": proc.memory_percent(),
                "num_threads": proc.num_threads(),
                "open_files": len(proc.open_files()),
                "connections": len(proc.connections()),
                "status": proc.status(),
                "create_time": proc.create_time(),
                "timestamp": time.time(),
            }
