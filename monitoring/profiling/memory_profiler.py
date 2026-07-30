from __future__ import annotations

import os
from typing import Any


class MemoryProfiler:
    """Memory-specific profiling with process and system details."""

    def sample(self) -> dict[str, Any]:
        try:
            import psutil
            virtual = psutil.virtual_memory()
            swap = psutil.swap_memory()
            process = psutil.Process()
            proc_mem = process.memory_info()
            proc_mem_full = process.memory_full_info()
        except ImportError:
            return {
                "rss_mb": 0.0,
                "vms_mb": 0.0,
                "available_mb": 0.0,
                "percent": 0.0,
                "note": "psutil not installed",
            }

        return {
            "rss_mb": proc_mem.rss / (1024 * 1024),
            "vms_mb": proc_mem.vms / (1024 * 1024),
            "available_mb": virtual.available / (1024 * 1024),
            "total_mb": virtual.total / (1024 * 1024),
            "percent": virtual.percent,
            "used_mb": virtual.used / (1024 * 1024),
            "free_mb": virtual.free / (1024 * 1024),
            "swap_total_mb": swap.total / (1024 * 1024),
            "swap_used_mb": swap.used / (1024 * 1024),
            "swap_percent": swap.percent,
            "uss_mb": getattr(proc_mem_full, "uss", 0) / (1024 * 1024),
            "pss_mb": getattr(proc_mem_full, "pss", 0) / (1024 * 1024),
            "unique_mb": proc_mem.rss / (1024 * 1024),
        }
