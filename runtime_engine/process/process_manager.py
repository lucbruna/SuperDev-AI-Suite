from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
import time
from typing import Any

logger = logging.getLogger(__name__)


class ManagedProcess:
    def __init__(self, pid: int, cmd: list[str], cwd: str | None, process: asyncio.subprocess.Process) -> None:
        self.pid = pid
        self.cmd = cmd
        self.cwd = cwd
        self._process = process
        self.created_at = time.time()
        self._status = "running"

    @property
    def status(self) -> str:
        if self._process.returncode is not None:
            return "completed"
        return self._status

    async def kill(self) -> None:
        if self._process.returncode is None:
            if sys.platform == "win32":
                self._process.kill()
            else:
                os.kill(self.pid, signal.SIGKILL)
            await self._process.wait()
            self._status = "killed"


class ProcessManager:
    def __init__(self) -> None:
        self._processes: dict[int, ManagedProcess] = {}

    async def create_process(
        self,
        cmd: list[str],
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> int:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env,
        )
        managed = ManagedProcess(proc.pid, cmd, cwd, proc)
        self._processes[proc.pid] = managed
        return proc.pid

    def get_process(self, pid: int) -> ManagedProcess | None:
        return self._processes.get(pid)

    async def kill_process(self, pid: int) -> bool:
        managed = self._processes.get(pid)
        if managed is None:
            return False
        await managed.kill()
        return True

    def list_processes(self) -> list[ManagedProcess]:
        return list(self._processes.values())

    def get_stats(self) -> dict[str, int]:
        all_procs = self._processes.values()
        return {
            "total": len(all_procs),
            "running": sum(1 for p in all_procs if p.status == "running"),
            "completed": sum(1 for p in all_procs if p.status == "completed"),
            "killed": sum(1 for p in all_procs if p.status == "killed"),
        }

    def active_count(self) -> int:
        return sum(1 for p in self._processes.values() if p.status == "running")

    async def shutdown_all(self) -> None:
        for pid, managed in list(self._processes.items()):
            await managed.kill()
        self._processes.clear()
