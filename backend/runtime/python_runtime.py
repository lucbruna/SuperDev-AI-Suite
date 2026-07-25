from __future__ import annotations

import asyncio
import os
import sys
import time
import tempfile
from pathlib import Path
from typing import AsyncIterator

from backend.runtime.base_runtime import (
    BaseRuntime,
    ExecutionResult,
    Language,
    ResourceLimits,
    RuntimeConfig,
    RuntimeStatus,
)
from backend.runtime.sandbox import sandbox_manager
from backend.utils.uuid_utils import generate_uuid


class PythonRuntime(BaseRuntime):
    """Python code execution runtime."""

    @property
    def language(self) -> Language:
        return Language.PYTHON

    @property
    def supported_extensions(self) -> list[str]:
        return [".py"]

    async def execute(
        self,
        config: RuntimeConfig,
        run_id: str,
    ) -> ExecutionResult:
        start_time = time.time()
        limits = config.resource_limits

        sandbox_dir = sandbox_manager.create_sandbox(run_id, limits)

        try:
            entry_file = config.filename or "main.py"
            await sandbox_manager.write_file(run_id, f"src/{entry_file}", config.code)

            cmd = [sys.executable, str(sandbox_dir / "src" / entry_file)]

            env = os.environ.copy()
            env.update(config.env_vars)
            env["PYTHONDONTWRITEBYTECODE"] = "1"

            if config.dependencies:
                pip_cmd = [sys.executable, "-m", "pip", "install", "--quiet"] + config.dependencies
                pip_proc = await asyncio.create_subprocess_exec(
                    *pip_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(sandbox_dir),
                )
                await pip_proc.communicate()

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

            if len(stdout) > limits.max_output_size_bytes:
                stdout = stdout[:limits.max_output_size_bytes] + "\n... (output truncated)"
            if len(stderr) > limits.max_output_size_bytes:
                stderr = stderr[:limits.max_output_size_bytes] + "\n... (output truncated)"

            execution_time = (time.time() - start_time) * 1000
            status = RuntimeStatus.COMPLETED if proc.returncode == 0 else RuntimeStatus.FAILED

            artifacts = []
            output_dir = sandbox_dir / "output"
            if output_dir.exists():
                for file in output_dir.rglob("*"):
                    if file.is_file():
                        artifacts.append({
                            "name": file.name,
                            "path": str(file.relative_to(sandbox_dir)),
                            "size": file.stat().st_size,
                        })

            return ExecutionResult(
                run_id=run_id,
                status=status,
                stdout=stdout,
                stderr=stderr,
                exit_code=proc.returncode,
                execution_time_ms=execution_time,
                artifacts=artifacts,
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
            entry_file = config.filename or "main.py"
            await sandbox_manager.write_file(run_id, f"src/{entry_file}", config.code)

            cmd = [sys.executable, "-u", str(sandbox_dir / "src" / entry_file)]

            env = os.environ.copy()
            env.update(config.env_vars)
            env["PYTHONUNBUFFERED"] = "1"
            env["PYTHONDONTWRITEBYTECODE"] = "1"

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
