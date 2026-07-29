from __future__ import annotations

import os
import signal
import threading
import time
from contextlib import contextmanager
from typing import Any, Generator


class SandboxResourceLimits:
    def __init__(
        self,
        max_cpu: int = 80,
        max_memory_mb: int = 500,
        max_disk_mb: int = 100,
        max_execution_time: int = 30,
    ) -> None:
        self.max_cpu = max_cpu
        self.max_memory_mb = max_memory_mb
        self.max_disk_mb = max_disk_mb
        self.max_execution_time = max_execution_time
        self._active = False

    @contextmanager
    def apply(self) -> Generator[None, None, None]:
        self._active = True
        timer = threading.Timer(self.max_execution_time, self._timeout_handler)
        timer.daemon = True
        timer.start()

        try:
            yield
        finally:
            timer.cancel()
            self._active = False

    def _timeout_handler(self) -> None:
        if self._active:
            main_thread = threading.main_thread()
            if main_thread.is_alive():
                raise TimeoutError(
                    f"Execution exceeded max time of {self.max_execution_time}s"
                )

    def get_resource_summary(self) -> dict[str, Any]:
        return {
            "max_cpu_percent": self.max_cpu,
            "max_memory_mb": self.max_memory_mb,
            "max_disk_mb": self.max_disk_mb,
            "max_execution_time_seconds": self.max_execution_time,
        }