from __future__ import annotations

import asyncio
import os
import time
from typing import AsyncIterator

from backend.runtime.base_runtime import (
    BaseRuntime,
    ExecutionResult,
    Language,
    RuntimeConfig,
    RuntimeStatus,
)
from backend.runtime.sandbox import sandbox_manager


class ShellRuntime(BaseRuntime):
    """Shell/Bash code execution runtime."""

    @property
    def language(self) -> Language:
        return Language.SHELL

    @property
    def supported_extensions(self) -> list[str]:
        return [".sh", ".bash"]

    async def execute(
        self,
        config: RuntimeConfig,
        run_id: str,
    ) -> ExecutionResult:
        start_time = time.time()
        limits = config.resource_limits
        sandbox_dir = sandbox_manager.create_sandbox(run_id, limits)

        try:
            entry_file = config.filename or "main.sh"
            script_content = f"#!/bin/bash\nset -euo pipefail\n{config.code}"
            await sandbox_manager.write_file(run_id, f"src/{entry_file}", script_content)

            cmd = ["bash", str(sandbox_dir / "src" / entry_file)]

            env = os.environ.copy()
            env.update(config.env_vars)

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(sandbox_dir / "src"),
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=limits.max_execution_time_seconds,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                execution_time = (time.time() - start_time) * 1000
                return ExecutionResult(
                    run_id=run_id,
                    status=RuntimeStatus.TIMEOUT,
                    execution_time_ms=execution_time,
                    error=f"Execution timed out after {limits.max_execution_time_seconds}s",
                )

            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")

            execution_time = (time.time() - start_time) * 1000
            status = RuntimeStatus.COMPLETED if proc.returncode == 0 else RuntimeStatus.FAILED

            return ExecutionResult(
                run_id=run_id,
                status=status,
                stdout=stdout,
                stderr=stderr,
                exit_code=proc.returncode,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                run_id=run_id,
                status=RuntimeStatus.FAILED,
                execution_time_ms=execution_time,
                error=str(e),
            )
        finally:
            sandbox_manager.cleanup_sandbox(run_id)

    async def stream(
        self,
        config: RuntimeConfig,
        run_id: str,
    ) -> AsyncIterator[str]:
        limits = config.resource_limits
        sandbox_dir = sandbox_manager.create_sandbox(run_id, limits)

        try:
            entry_file = config.filename or "main.sh"
            script_content = f"#!/bin/bash\nset -euo pipefail\n{config.code}"
            await sandbox_manager.write_file(run_id, f"src/{entry_file}", script_content)

            cmd = ["bash", str(sandbox_dir / "src" / entry_file)]

            env = os.environ.copy()
            env.update(config.env_vars)

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env,
                cwd=str(sandbox_dir / "src"),
            )

            try:
                async with asyncio.timeout(limits.max_execution_time_seconds):
                    async for line in proc.stdout:
                        yield line.decode("utf-8", errors="replace")
            except asyncio.TimeoutError:
                proc.kill()
                yield f"\n[TIMEOUT] Execution timed out after {limits.max_execution_time_seconds}s\n"
            finally:
                await proc.wait()

        finally:
            sandbox_manager.cleanup_sandbox(run_id)
