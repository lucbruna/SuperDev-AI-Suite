from __future__ import annotations

import os
from typing import Any

from ..monitoring_models import MetricSample, MetricType


class CpuMetrics:
    """CPU utilisation metrics."""

    @staticmethod
    def collect() -> list[MetricSample]:
        samples: list[MetricSample] = []
        try:
            # Cross-platform via /proc/stat (Linux) fallback
            if os.name == "posix":
                with open("/proc/stat") as f:
                    line = f.readline()
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        user = int(parts[1])
                        nice = int(parts[2])
                        system = int(parts[3])
                        idle = int(parts[4])
                        total = user + nice + system + idle
                        samples.append(MetricSample("cpu_user", float(user), metric_type=MetricType.COUNTER))
                        samples.append(MetricSample("cpu_system", float(system), metric_type=MetricType.COUNTER))
                        samples.append(MetricSample("cpu_idle", float(idle), metric_type=MetricType.COUNTER))
                        samples.append(MetricSample("cpu_total", float(total), metric_type=MetricType.COUNTER))
        except Exception:
            pass
        return samples


__all__ = ["CpuMetrics"]
