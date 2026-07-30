from __future__ import annotations

import time
from typing import Any


class NetworkProfiler:
    """Network-specific profiling with bandwidth tracking."""

    def __init__(self) -> None:
        self._last_rx: int = 0
        self._last_tx: int = 0
        self._last_time: float = 0.0

    def sample(self) -> dict[str, Any]:
        try:
            import psutil
            net = psutil.net_io_counters()
            connections = len(psutil.net_connections())
        except ImportError:
            return {
                "bytes_sent": 0,
                "bytes_recv": 0,
                "send_speed": 0,
                "recv_speed": 0,
                "connections": 0,
            }

        now = time.time()
        rx = int(net.bytes_recv)
        tx = int(net.bytes_sent)

        if self._last_time and (now - self._last_time) > 0:
            dt = now - self._last_time
            rx_speed = (rx - self._last_rx) / dt
            tx_speed = (tx - self._last_tx) / dt
        else:
            rx_speed = 0.0
            tx_speed = 0.0

        self._last_rx = rx
        self._last_tx = tx
        self._last_time = now

        return {
            "bytes_sent": tx,
            "bytes_recv": rx,
            "send_speed_bps": tx_speed,
            "recv_speed_bps": rx_speed,
            "send_speed_mbps": tx_speed / (1024 * 1024),
            "recv_speed_mbps": rx_speed / (1024 * 1024),
            "total_mb_sent": tx / (1024 * 1024),
            "total_mb_recv": rx / (1024 * 1024),
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
            "errin": net.errin,
            "errout": net.errout,
            "dropin": net.dropin,
            "dropout": net.dropout,
            "connections": connections,
        }
