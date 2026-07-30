from __future__ import annotations

import os
from typing import Any

from ..monitoring_models import MetricSample, MetricType


class MemoryMetrics:
    """Memory utilisation metrics."""

    @staticmethod
    def collect() -> list[MetricSample]:
        samples: list[MetricSample] = []
        try:
            if os.name == "posix":
                with open("/proc/meminfo") as f:
                    meminfo: dict[str, int] = {}
                    for line in f:
                        parts = line.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val_str = parts[1].strip().split()[0]
                            meminfo[key] = int(val_str)
                if "MemTotal" in meminfo:
                    total = meminfo["MemTotal"]
                    free = meminfo.get("MemFree", 0)
                    available = meminfo.get("MemAvailable", 0)
                    used = total - available
                    samples.append(MetricSample("mem_total_kb", float(total), metric_type=MetricType.GAUGE))
                    samples.append(MetricSample("mem_used_kb", float(used), metric_type=MetricType.GAUGE))
                    samples.append(MetricSample("mem_free_kb", float(free), metric_type=MetricType.GAUGE))
                    samples.append(MetricSample("mem_available_kb", float(available), metric_type=MetricType.GAUGE))
        except Exception:
            pass
        return samples


__all__ = ["MemoryMetrics"]
