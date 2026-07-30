from __future__ import annotations

import time
from typing import Any


class NetworkCollector:
    """Collects network I/O metrics."""

    def collect(self) -> dict[str, Any]:
        import psutil
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
            "err_in": net.errin,
            "err_out": net.errout,
            "drop_in": net.dropin,
            "drop_out": net.dropout,
            "timestamp": time.time(),
        }
