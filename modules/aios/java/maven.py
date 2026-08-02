"""Maven build wrapper for the AIOS java runtime."""
from __future__ import annotations

import asyncio
from typing import Any

from modules.aios.java.java_client import require_java_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class MavenUnavailableError(RuntimeError):
    """Raised when the mvn CLI cannot be reached (not installed)."""


class MavenManager:
    """Runs maven lifecycle phases via the mvn CLI."""

    def __init__(self, binary: str = "mvn") -> None:
        self.binary = binary
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(
        self, args: list[str], *, cwd: str | None = None, timeout_s: float = 600.0
    ) -> tuple[int, str, str]:
        try:
            proc = await asyncio.create_subprocess_exec(
                self.binary,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
        except FileNotFoundError as exc:
            raise MavenUnavailableError(f"mvn CLI not found: {self.binary}") from exc
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise MavenUnavailableError(
                f"mvn {' '.join(args[:3])} timed out after {timeout_s}s"
            ) from None
        return (
            int(proc.returncode or 0),
            out_b.decode("utf-8", errors="replace"),
            err_b.decode("utf-8", errors="replace"),
        )

    async def version(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_java_action("maven")
        code, out, err = await self._run(["--version"], cwd=cwd, timeout_s=60.0)
        if code != 0:
            raise MavenUnavailableError(
                f"mvn --version failed: {err.strip() or out.strip()}"
            )
        version = next(
            (line.split()[2] for line in out.splitlines() if line.strip().startswith("Apache Maven")),
            out.strip(),
        )
        return {"version": version}

    async def build(
        self, *, cwd: str | None = None, phases: list[str] | None = None
    ) -> dict[str, Any]:
        require_java_action("maven")
        args = phases or ["compile"]
        code, out, err = await self._run(args, cwd=cwd)
        self._metrics.increment("java.maven.build")
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def test(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_java_action("maven")
        code, out, err = await self._run(["test"], cwd=cwd)
        self._metrics.increment("java.maven.test")
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["MavenManager", "MavenUnavailableError"]
