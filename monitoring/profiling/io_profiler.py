from __future__ import annotations

from typing import Any


class IoProfiler:
    """I/O-specific profiling for disk read/write operations."""

    def __init__(self) -> None:
        self._last_read: int = 0
        self._last_write: int = 0
        self._last_time: float = 0.0

    def sample(self) -> dict[str, Any]:
        import time
        try:
            import psutil
            io = psutil.disk_io_counters()
            proc = psutil.Process()
            proc_io = proc.io_counters()
        except ImportError:
            return {
                "read_bytes": 0,
                "write_bytes": 0,
                "read_speed": 0,
                "write_speed": 0,
            }

        now = time.time()
        read_bytes = int(io.read_bytes) if io else 0
        write_bytes = int(io.write_bytes) if io else 0

        if self._last_time and (now - self._last_time) > 0:
            dt = now - self._last_time
            read_speed = (read_bytes - self._last_read) / dt
            write_speed = (write_bytes - self._last_write) / dt
        else:
            read_speed = 0.0
            write_speed = 0.0

        self._last_read = read_bytes
        self._last_write = write_bytes
        self._last_time = now

        return {
            "read_bytes": read_bytes,
            "write_bytes": write_bytes,
            "read_speed_bps": read_speed,
            "write_speed_bps": write_speed,
            "read_speed_mbps": read_speed / (1024 * 1024),
            "write_speed_mbps": write_speed / (1024 * 1024),
            "process_read_bytes": int(proc_io.read_bytes) if proc_io else 0,
            "process_write_bytes": int(proc_io.write_bytes) if proc_io else 0,
            "io_in_progress": getattr(io, 'busy_time', 0) if io else 0,
            "read_count": int(io.read_count) if io else 0,
            "write_count": int(io.write_count) if io else 0,
        }
