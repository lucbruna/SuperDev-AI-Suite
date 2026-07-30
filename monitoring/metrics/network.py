from __future__ import annotations

import os
from typing import Any

from ..monitoring_models import MetricSample, MetricType


class NetworkMetrics:
    """Network I/O metrics from ``/proc/net/dev`` (Linux)."""

    @staticmethod
    def collect() -> list[MetricSample]:
        samples: list[MetricSample] = []
        try:
            if os.name == "posix":
                with open("/proc/net/dev") as f:
                    next(f)  # header
                    next(f)  # header
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 10:
                            iface = parts[0].rstrip(":")
                            rx_bytes = int(parts[1])
                            tx_bytes = int(parts[9])
                            samples.append(MetricSample(
                                "net_rx_bytes", float(rx_bytes),
                                labels={"interface": iface}, metric_type=MetricType.COUNTER,
                            ))
                            samples.append(MetricSample(
                                "net_tx_bytes", float(tx_bytes),
                                labels={"interface": iface}, metric_type=MetricType.COUNTER,
                            ))
        except Exception:
            pass
        return samples


__all__ = ["NetworkMetrics"]
