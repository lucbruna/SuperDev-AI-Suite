"""Process monitor — observe and collect metrics from running processes."""
from __future__ import annotations

import asyncio
import psutil
from dataclasses import dataclass

from modules.aios import get_kernel_logger, get_kernel_metrics
from modules.aios.process.acl import require_process_action


@dataclass
class ProcessMetrics:
    """Metrics snapshot for a process."""
    pid: int
    cpu_percent: float
    memory_mb: float
    num_threads: int
    status: str
    create_time: float


class ProcessMonitor:
    """Monitor system processes and collect metrics."""

    def __init__(self, interval: float = 1.0) -> None:
        self._interval = interval
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()
        self._monitoring = False
        self._task: asyncio.Task | None = None

    async def start(self, pids: list[int] | None = None) -> None:
        """Start monitoring processes."""
        require_process_action("monitor")
        self._monitoring = True
        self._pids = pids or []
        self._task = asyncio.create_task(self._monitor_loop())
        self._logger.log("process", f"monitor started for {len(self._pids)} pids")

    async def stop(self) -> None:
        """Stop monitoring."""
        require_process_action("monitor")
        self._monitoring = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._logger.log("process", "monitor stopped")

    async def _monitor_loop(self) -> None:
        while self._monitoring:
            for pid in self._pids:
                try:
                    proc = psutil.Process(pid)
                    metrics = ProcessMetrics(
                        pid=pid,
                        cpu_percent=proc.cpu_percent(),
                        memory_mb=proc.memory_info().rss / 1024 / 1024,
                        num_threads=proc.num_threads(),
                        status=proc.status(),
                        create_time=proc.create_time(),
                    )
                    self._metrics.set_gauge(f"process.{pid}.cpu", metrics.cpu_percent)
                    self._metrics.set_gauge(f"process.{pid}.memory_mb", metrics.memory_mb)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            await asyncio.sleep(self._interval)

    def snapshot(self, pid: int) -> ProcessMetrics | None:
        """Get a one-time metrics snapshot for a PID."""
        require_process_action("monitor")
        try:
            proc = psutil.Process(pid)
            return ProcessMetrics(
                pid=pid,
                cpu_percent=proc.cpu_percent(),
                memory_mb=proc.memory_info().rss / 1024 / 1024,
                num_threads=proc.num_threads(),
                status=proc.status(),
                create_time=proc.create_time(),
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def list_system_processes(self, filter_name: str | None = None) -> list[ProcessMetrics]:
        """List all system processes, optionally filtered by name."""
        require_process_action("monitor")
        results = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "num_threads", "status", "create_time"]):
            try:
                info = proc.info
                if filter_name and filter_name.lower() not in (info["name"] or "").lower():
                    continue
                results.append(ProcessMetrics(
                    pid=info["pid"],
                    cpu_percent=info["cpu_percent"] or 0,
                    memory_mb=info["memory_info"].rss / 1024 / 1024 if info["memory_info"] else 0,
                    num_threads=info["num_threads"] or 0,
                    status=info["status"] or "unknown",
                    create_time=info["create_time"] or 0,
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return results


__all__ = ["ProcessMonitor", "ProcessMetrics"]
