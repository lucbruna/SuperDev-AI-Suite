from __future__ import annotations

import asyncio
import json
import shutil
from typing import Any

from runtime_engine.runtime.runtime import BaseRuntime, ExecutionResult
from runtime_engine.core.configuration import RuntimeConfig


class DockerClient:
    def __init__(self) -> None:
        self._docker_path = shutil.which("docker")

    async def run_container(
        self,
        image: str,
        command: list[str] | None = None,
        remove: bool = True,
        volumes: dict[str, str] | None = None,
        env: dict[str, str] | None = None,
        timeout: int = 30,
    ) -> ExecutionResult:
        if not self._docker_path:
            return ExecutionResult(exit_code=-1, stdout="", stderr="Docker not found", duration=0.0, error="Docker CLI missing")
        cmd = [self._docker_path, "run"]
        if remove:
            cmd.append("--rm")
        if volumes:
            for host, container in volumes.items():
                cmd.extend(["-v", f"{host}:{container}"])
        if env:
            for k, v in env.items():
                cmd.extend(["-e", f"{k}={v}"])
        cmd.append(image)
        if command:
            cmd.extend(command)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return ExecutionResult(
                exit_code=proc.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                duration=0.0,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return ExecutionResult(exit_code=-1, stdout="", stderr="Docker timeout", duration=0.0, error="Timeout")

    async def stop_container(self, container_id: str) -> bool:
        if not self._docker_path:
            return False
        proc = await asyncio.create_subprocess_exec(
            self._docker_path, "stop", container_id,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()
        return proc.returncode == 0

    async def exec_in_container(self, container_id: str, command: list[str]) -> ExecutionResult:
        if not self._docker_path:
            return ExecutionResult(exit_code=-1, stdout="", stderr="Docker not found", duration=0.0, error="Docker CLI missing")
        proc = await asyncio.create_subprocess_exec(
            self._docker_path, "exec", container_id, *command,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return ExecutionResult(
            exit_code=proc.returncode or 0,
            stdout=stdout.decode("utf-8", errors="replace"),
            stderr=stderr.decode("utf-8", errors="replace"),
            duration=0.0,
        )

    async def get_logs(self, container_id: str) -> str:
        if not self._docker_path:
            return ""
        proc = await asyncio.create_subprocess_exec(
            self._docker_path, "logs", container_id,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        return stdout.decode("utf-8", errors="replace")


class DockerRuntime(BaseRuntime):
    def __init__(self, config: RuntimeConfig | None = None) -> None:
        super().__init__(config)
        self._client = DockerClient()

    async def execute(
        self,
        code: str,
        language: str = "python",
        config: RuntimeConfig | None = None,
        image: str = "python:3.11-slim",
    ) -> ExecutionResult:
        return await self._client.run_container(
            image=image,
            command=["python3", "-c", code],
            timeout=config.default_timeout if config else self.config.default_timeout,
        )

    async def execute_in_image(
        self,
        image: str,
        command: list[str],
        timeout: int = 30,
    ) -> ExecutionResult:
        return await self._client.run_container(
            image=image,
            command=command,
            timeout=timeout,
        )
