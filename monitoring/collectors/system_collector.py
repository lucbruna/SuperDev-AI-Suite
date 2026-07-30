from __future__ import annotations

import os
import platform
import time
from typing import Any


class SystemCollector:
    """Collects system-level metrics."""

    def collect(self) -> dict[str, Any]:
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "cpus": os.cpu_count() or 0,
            "pid": os.getpid(),
            "timestamp": time.time(),
        }
