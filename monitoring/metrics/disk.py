from __future__ import annotations

import os
import shutil
from typing import Any

from ..monitoring_models import MetricSample, MetricType


class DiskMetrics:
    """Disk utilisation metrics via ``shutil.disk_usage``."""

    @staticmethod
    def collect(path: str = "/") -> list[MetricSample]:
        samples: list[MetricSample] = []
        try:
            usage = shutil.disk_usage(path)
            samples.append(MetricSample("disk_total_bytes", float(usage.total), labels={"path": path}, metric_type=MetricType.GAUGE))
            samples.append(MetricSample("disk_used_bytes", float(usage.used), labels={"path": path}, metric_type=MetricType.GAUGE))
            samples.append(MetricSample("disk_free_bytes", float(usage.free), labels={"path": path}, metric_type=MetricType.GAUGE))
            pct = (usage.used / usage.total * 100) if usage.total > 0 else 0.0
            samples.append(MetricSample("disk_usage_pct", round(pct, 2), labels={"path": path}, metric_type=MetricType.GAUGE))
        except Exception:
            pass
        return samples


__all__ = ["DiskMetrics"]
