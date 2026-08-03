"""Process manager — spawn, track, and manage subprocesses."""
from __future__ import annotations

import asyncio
import os
import signal
import sys
from dataclasses import dataclass
from time import monotonic

from modules.aios import get_kernel_logger, get_kernel_metrics
from modules.aios.process.acl import require_process_action


@dataclass
class ProcessInfo:
    """Information about a managed process."""
    pid: int
    cmd: list[str]
    cwd: str
    start_time: float
    status: str = "running"
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""


class ProcessManager:
    """Manages subprocess lifecycle with kernel integration."""

    def __init__(self) -> None:
        self._processes: dict[int, ProcessInfo] = {}
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def spawn(
        self,
        cmd: list[str],
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> ProcessInfo:
        """Spawn a new subprocess."""
        require_process_action("spawn")
        started = monotonic()
        cwd = cwd or os.getcwd()

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            env={**os.environ, **(env or {})},
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        info = ProcessInfo(
            pid=proc.pid,
            cmd=cmd,
            cwd=cwd,
            start_time=started,
        )
        self._processes[proc.pid] = info

        # Capture output in background
        asyncio.create_task(self._capture_output(proc, info))

        self._logger.log("process", f"spawned: pid={proc.pid} cmd={' '.join(cmd)}")
        self._metrics.record_timing("process.spawn", monotonic() - started)
        return info

    async def _capture_output(self, proc: asyncio.subprocess.Process, info: ProcessInfo) -> None:
        stdout, stderr = await proc.communicate()
        info.stdout = stdout.decode(errors="replace")
        info.stderr = stderr.decode(errors="replace")
        info.returncode = proc.returncode
        info.status = "completed" if proc.returncode == 0 else "failed"
        self._logger.log("process", f"completed: pid={proc.pid} rc={proc.returncode}")

    def get(self, pid: int) -> ProcessInfo | None:
        """Get process info by PID."""
        return self._processes.get(pid)

    def list(self) -> list[ProcessInfo]:
        """List all managed processes."""
        return list(self._processes.values())

    async def wait(self, pid: int, timeout: float | None = None) -> ProcessInfo:
        """Wait for a process to complete."""
        info = self._processes.get(pid)
        if not info:
            raise ProcessError(f"Process {pid} not found")
        # The background task already captures output; just wait
        while info.status == "running":
            await asyncio.sleep(0.1)
            if timeout is not None:
                timeout -= 0.1
                if timeout <= 0:
                    raise ProcessError(f"Timeout waiting for process {pid}")
        return info

    async def terminate(self, pid: int, force: bool = False) -> bool:
        """Terminate a process."""
        require_process_action("terminate")
        info = self._processes.get(pid)
        if not info:
            return False

        try:
            if sys.platform == "win32":
                os.kill(pid, signal.CTRL_BREAK_EVENT if not force else signal.SIGTERM)
            else:
                os.kill(pid, signal.SIGTERM if not force else signal.SIGKILL)
            info.status = "terminated"
            self._logger.log("process", f"terminated: pid={pid}")
            return True
        except ProcessLookupError:
            return False


class ProcessError(Exception):
    """Process manager error."""
    pass


__all__ = ["ProcessManager", "ProcessInfo", "ProcessError"]
