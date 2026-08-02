"""Python poetry manager — dependency management via the poetry CLI."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.python.venv_manager import require_python_action


class PoetryUnavailableError(RuntimeError):
    """Raised when the poetry CLI is not installed."""


class PoetryManager:
    """Project dependency lifecycle via ``poetry`` (degrades gracefully)."""

    def __init__(self, binary: str = "poetry") -> None:
        self.binary = binary
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(
        self, args: list[str], *, cwd: str | Path | None = None, timeout_s: float = 300.0
    ) -> tuple[int, str, str]:
        try:
            proc = await asyncio.create_subprocess_exec(
                self.binary,
                *args,
                cwd=str(cwd) if cwd else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise PoetryUnavailableError(f"poetry CLI not found: {self.binary}") from exc
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise PoetryUnavailableError(f"poetry timed out after {timeout_s}s") from None
        return (
            int(proc.returncode or 0),
            out_b.decode("utf-8", errors="replace"),
            err_b.decode("utf-8", errors="replace"),
        )

    async def version(self) -> dict[str, Any]:
        code, out, err = await self._run(["--version"], timeout_s=30.0)
        if code != 0:
            raise PoetryUnavailableError(f"poetry --version failed: {err.strip() or out.strip()}")
        return {"version": out.strip()}

    async def install(self, project_dir: str | Path) -> dict[str, Any]:
        require_python_action("poetry")
        code, out, err = await self._run(["install"], cwd=project_dir)
        self._metrics.increment("python.poetry.install")
        return {
            "project": str(project_dir),
            "ok": code == 0,
            "error": err.strip() if code else "",
            "output": out.strip()[:500],
        }

    async def add(self, project_dir: str | Path, package: str) -> dict[str, Any]:
        require_python_action("poetry")
        code, _, err = await self._run(["add", package], cwd=project_dir)
        self._metrics.increment("python.poetry.add")
        return {
            "project": str(project_dir),
            "package": package,
            "ok": code == 0,
            "error": err.strip() if code else "",
        }

    async def lock(self, project_dir: str | Path) -> dict[str, Any]:
        require_python_action("poetry")
        code, _, err = await self._run(["lock"], cwd=project_dir)
        self._metrics.increment("python.poetry.lock")
        return {
            "project": str(project_dir),
            "ok": code == 0,
            "error": err.strip() if code else "",
        }


__all__ = ["PoetryManager", "PoetryUnavailableError"]
