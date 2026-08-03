"""Process cleanup — terminate orphaned processes and clean resources."""
from __future__ import annotations

import os
import signal
import sys
from dataclasses import dataclass
from time import monotonic

from modules.aios import get_kernel_logger, get_kernel_metrics
from modules.aios.process.acl import require_process_action


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""
    terminated: list[int]
    failed: list[int]
    duration: float


class ProcessCleanup:
    """Clean up orphaned or stale processes."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def cleanup_by_name(self, name: str, force: bool = False) -> CleanupResult:
        """Terminate all processes matching name."""
        require_process_action("cleanup")
        started = monotonic()
        import psutil

        terminated = []
        failed = []

        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                info = proc.info
                if name.lower() in (info["name"] or "").lower():
                    pid = info["pid"]
                    if await self._terminate_pid(pid, force):
                        terminated.append(pid)
                    else:
                        failed.append(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        duration = monotonic() - started
        self._logger.log("process", f"cleanup by name '{name}': terminated={len(terminated)} failed={len(failed)}")
        self._metrics.record_timing("process.cleanup_by_name", duration)
        return CleanupResult(terminated=terminated, failed=failed, duration=duration)

    async def cleanup_by_pid(self, pid: int, force: bool = False) -> CleanupResult:
        """Terminate a specific PID."""
        require_process_action("cleanup")
        started = monotonic()
        terminated = []
        failed = []

        if await self._terminate_pid(pid, force):
            terminated.append(pid)
        else:
            failed.append(pid)

        duration = monotonic() - started
        self._logger.log("process", f"cleanup by pid {pid}: {'ok' if terminated else 'failed'}")
        self._metrics.record_timing("process.cleanup_by_pid", duration)
        return CleanupResult(terminated=terminated, failed=failed, duration=duration)

    async def cleanup_children(self, parent_pid: int, force: bool = False) -> CleanupResult:
        """Terminate all children of a parent process."""
        require_process_action("cleanup")
        started = monotonic()
        import psutil

        terminated = []
        failed = []

        try:
            parent = psutil.Process(parent_pid)
            children = parent.children(recursive=True)
            for child in children:
                if await self._terminate_pid(child.pid, force):
                    terminated.append(child.pid)
                else:
                    failed.append(child.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        duration = monotonic() - started
        self._logger.log("process", f"cleanup children of {parent_pid}: terminated={len(terminated)} failed={len(failed)}")
        self._metrics.record_timing("process.cleanup_children", duration)
        return CleanupResult(terminated=terminated, failed=failed, duration=duration)

    async def cleanup_orphans(self, max_age_seconds: float = 3600, force: bool = False) -> CleanupResult:
        """Terminate processes older than max_age_seconds with no parent (orphans)."""
        require_process_action("cleanup")
        started = monotonic()
        import psutil
        import time

        terminated = []
        failed = []
        now = time.time()

        for proc in psutil.process_iter(["pid", "ppid", "create_time", "name"]):
            try:
                info = proc.info
                age = now - info["create_time"]
                if age > max_age_seconds:
                    # Check if parent exists
                    try:
                        psutil.Process(info["ppid"])
                    except psutil.NoSuchProcess:
                        # Orphan
                        if await self._terminate_pid(info["pid"], force):
                            terminated.append(info["pid"])
                        else:
                            failed.append(info["pid"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        duration = monotonic() - started
        self._logger.log("process", f"cleanup orphans: terminated={len(terminated)} failed={len(failed)}")
        self._metrics.record_timing("process.cleanup_orphans", duration)
        return CleanupResult(terminated=terminated, failed=failed, duration=duration)

    async def _terminate_pid(self, pid: int, force: bool) -> bool:
        """Terminate a single PID."""
        try:
            if sys.platform == "win32":
                os.kill(pid, signal.CTRL_BREAK_EVENT if not force else signal.SIGTERM)
            else:
                os.kill(pid, signal.SIGTERM if not force else signal.SIGKILL)
            return True
        except (ProcessLookupError, PermissionError):
            return False


__all__ = ["ProcessCleanup", "CleanupResult"]
