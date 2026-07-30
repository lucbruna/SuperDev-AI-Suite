from __future__ import annotations

import time
from typing import Any


class DiskCollector:
    """Collects disk I/O and usage metrics."""

    def collect(self) -> dict[str, Any]:
        import psutil
        disk_io = psutil.disk_io_counters()
        disk_usage = psutil.disk_usage("/")
        return {
            "read_bytes": disk_io.read_bytes if disk_io else 0,
            "write_bytes": disk_io.write_bytes if disk_io else 0,
            "read_count": disk_io.read_count if disk_io else 0,
            "write_count": disk_io.write_count if disk_io else 0,
            "total": disk_usage.total,
            "used": disk_usage.used,
            "free": disk_usage.free,
            "percent": disk_usage.percent,
            "timestamp": time.time(),
        }
