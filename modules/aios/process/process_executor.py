"""Process executor — high-level process execution with result handling."""
from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass
from time import monotonic

from modules.aios import get_kernel_logger, get_kernel_metrics
from modules.aios.process.acl import require_process_action


@dataclass
class ExecutionResult:
    """Result of a process execution."""
    returncode: int
    stdout: str
    stderr: str
    duration: float
    pid: int


class ProcessExecutor:
    """Execute processes with standardized result handling."""

    def __init__(self, default_timeout: float = 30.0) -> None:
        self._default_timeout = default_timeout
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def run(
        self,
        cmd: list[str],
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
        input_data: str | None = None,
    ) -> ExecutionResult:
        """Run a command and return structured result."""
        require_process_action("execute")
        started = monotonic()
        timeout = timeout or self._default_timeout
        cwd = cwd or os.getcwd()

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            env={**os.environ, **(env or {})},
            stdin=asyncio.subprocess.PIPE if input_data else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(input_data.encode() if input_data else None),
                timeout=timeout,
            )
        except TimeoutError:
            proc.kill()
            await proc.wait()
            duration = monotonic() - started
            self._logger.log("process", f"timeout: pid={proc.pid} cmd={' '.join(cmd)}")
            return ExecutionResult(
                returncode=-1,
                stdout="",
                stderr=f"Process timed out after {timeout}s",
                duration=duration,
                pid=proc.pid,
            )

        duration = monotonic() - started
        result = ExecutionResult(
            returncode=proc.returncode or 0,
            stdout=stdout_bytes.decode(errors="replace"),
            stderr=stderr_bytes.decode(errors="replace"),
            duration=duration,
            pid=proc.pid,
        )

        self._logger.log("process", f"executed: pid={proc.pid} rc={result.returncode} dur={duration:.3f}s")
        self._metrics.record_timing("process.execute", duration)
        return result

    async def run_shell(
        self,
        command: str,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> ExecutionResult:
        """Run a shell command."""
        require_process_action("execute")
        if sys.platform == "win32":
            return await self.run(["cmd", "/c", command], cwd, env, timeout)
        return await self.run(["sh", "-c", command], cwd, env, timeout)


__all__ = ["ProcessExecutor", "ExecutionResult"]
