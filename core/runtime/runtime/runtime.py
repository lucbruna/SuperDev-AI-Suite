from __future__ import annotations

import time
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator

from pydantic import BaseModel
from runtime_engine.core.configuration import RuntimeConfig


class ExecutionResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    error: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class BaseRuntime(ABC):
    def __init__(self, config: RuntimeConfig | None = None) -> None:
        self.config = config or RuntimeConfig()
        self._status: str = "idle"
        self._process: asyncio.subprocess.Process | None = None

    @abstractmethod
    async def execute(self, code: str, language: str, config: RuntimeConfig | None = None) -> ExecutionResult:
        pass

    async def abort(self) -> None:
        if self._process and self._process.returncode is None:
            self._process.kill()
            await self._process.wait()
            self._status = "aborted"

    def get_status(self) -> str:
        return self._status

    async def stream_logs(self) -> AsyncIterator[str]:
        yield "Streaming not implemented for this runtime"

    async def _run_subprocess(
        self,
        cmd: list[str],
        input_data: str | None = None,
        timeout: int | None = None,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> ExecutionResult:
        start = time.monotonic()
        started_at = datetime.utcnow()
        try:
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )
            encoded = input_data.encode("utf-8") if input_data else None
            try:
                stdout, stderr = await asyncio.wait_for(
                    self._process.communicate(encoded), timeout=timeout or self.config.default_timeout
                )
            except asyncio.TimeoutError:
                self._process.kill()
                await self._process.wait()
                duration = time.monotonic() - start
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr="Process timed out",
                    duration=duration,
                    error="Timeout",
                    started_at=started_at,
                    finished_at=datetime.utcnow(),
                )
            duration = time.monotonic() - start
            self._status = "completed"
            return ExecutionResult(
                exit_code=self._process.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace") if stdout else "",
                stderr=stderr.decode("utf-8", errors="replace") if stderr else "",
                duration=duration,
                started_at=started_at,
                finished_at=datetime.utcnow(),
            )
        except Exception as e:
            duration = time.monotonic() - start
            self._status = "failed"
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration=duration,
                error=str(e),
                started_at=started_at,
                finished_at=datetime.utcnow(),
            )
