"""Docker client — low-level wrapper around the docker CLI."""
from __future__ import annotations

import asyncio
import json
from time import monotonic
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    get_kernel_security,
)


class DockerUnavailableError(RuntimeError):
    """Raised when the docker CLI or daemon cannot be reached."""


def require_docker_action(action: str) -> None:
    """Enforce the ``docker:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("docker", action):
        raise KernelPermissionDeniedError("docker", action)


class DockerClient:
    """Spawns the ``docker`` CLI as a subprocess (no SDK dependency).

    Every call is async and times out; CLI/daemon failures surface as
    :class:`DockerUnavailableError` so callers can degrade gracefully.
    """

    def __init__(self, binary: str = "docker") -> None:
        self.binary = binary
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(
        self, args: list[str], *, timeout_s: float | None = 120.0
    ) -> tuple[int, str, str]:
        """Run the CLI without a shell; return (returncode, stdout, stderr)."""
        started = monotonic()
        try:
            proc = await asyncio.create_subprocess_exec(
                self.binary,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise DockerUnavailableError(
                f"docker CLI not found: {self.binary}"
            ) from exc
        try:
            stdout_b, stderr_b = await asyncio.wait_for(
                proc.communicate(), timeout=timeout_s
            )
        except TimeoutError:
            proc.kill()
            raise DockerUnavailableError(
                f"docker {' '.join(args[:3])} timed out after {timeout_s}s"
            ) from None
        stdout = stdout_b.decode("utf-8", errors="replace")
        stderr = stderr_b.decode("utf-8", errors="replace")
        self._metrics.record_timing("docker.cli", monotonic() - started)
        returncode = int(proc.returncode or 0)
        self._logger.log(
            "docker", f"cli: docker {' '.join(args[:3])} -> {returncode}"
        )
        return returncode, stdout, stderr

    @staticmethod
    def first_json(text: str) -> dict[str, Any]:
        """Parse the first JSON object in ``--format '{{json .}}'`` output."""
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
        raise ValueError(f"no JSON object in docker output: {text[:200]!r}")

    @staticmethod
    def json_lines(text: str) -> list[dict[str, Any]]:
        """Parse every JSON-object line (one object per container/image/etc)."""
        rows: list[dict[str, Any]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                rows.append(parsed)
        return rows

    async def version(self) -> dict[str, Any]:
        require_docker_action("inspect")
        code, out, err = await self._run(
            ["version", "--format", "{{json .}}"], timeout_s=30.0
        )
        if code != 0:
            raise DockerUnavailableError(
                f"docker version failed: {err.strip() or out.strip()}"
            )
        return self.first_json(out)

    async def ping(self) -> bool:
        try:
            code, _, _ = await self._run(["info"], timeout_s=30.0)
            return code == 0
        except DockerUnavailableError:
            return False

    async def info(self) -> dict[str, Any]:
        require_docker_action("inspect")
        code, out, err = await self._run(
            ["info", "--format", "{{json .}}"], timeout_s=30.0
        )
        if code != 0:
            raise DockerUnavailableError(
                f"docker info failed: {err.strip() or out.strip()}"
            )
        return self.first_json(out)


__all__ = ["DockerClient", "DockerUnavailableError", "require_docker_action"]
