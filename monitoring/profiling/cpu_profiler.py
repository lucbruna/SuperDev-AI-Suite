from __future__ import annotations

import os
import time
from typing import Any


class CpuProfiler:
    """CPU-specific profiling with per-process and system-wide metrics."""

    def __init__(self) -> None:
        self._last_cpu = 0.0
        self._last_time = 0.0
        self._samples: list[float] = []

    def sample(self) -> dict[str, Any]:
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            per_cpu = psutil.cpu_percent(interval=0.0, percpu=True)
            process = psutil.Process()
            proc_cpu = process.cpu_percent(interval=0.0)
            ctx_switches = process.num_ctx_switches()
            threads = process.num_threads()
        except ImportError:
            cpu_percent = 0.0
            per_cpu = []
            proc_cpu = 0.0
            ctx_switches = None
            threads = 0

        now = time.time()
        if self._last_cpu:
            load = cpu_percent / 100.0
        else:
            load = 0.0
        self._last_cpu = cpu_percent
        self._last_time = now
        self._samples.append(cpu_percent)

        return {
            "cpu_percent": cpu_percent,
            "per_cpu": per_cpu,
            "process_cpu": proc_cpu,
            "cpu_count": os.cpu_count() or 0,
            "load": load,
            "context_switches": ctx_switches,
            "threads": threads,
            "samples_count": len(self._samples),
            "avg_cpu": sum(self._samples[-100:]) / max(len(self._samples[-100:]), 1),
        }
