"""Python uv manager — fast dependency/venv management via the uv CLI."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.python.venv_manager import require_python_action


class UvUnavailableError(RuntimeError):
    """Raised when the uv CLI is not installed."""


class UvManager:
    """Fast env/package lifecycle via ``uv`` (degrades gracefully)."""

    def __init__(self, binary: str = "uv") -> None:
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
            raise UvUnavailableError(f"uv CLI not found: {self.binary}") from exc
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise UvUnavailableError(f"uv timed out after {timeout_s}s") from None
        return (
            int(proc.returncode or 0),
            out_b.decode("utf-8", errors="replace"),
            err_b.decode("utf-8", errors="replace"),
        )

    async def version(self) -> dict[str, Any]:
        code, out, err = await self._run(["--version"], timeout_s=30.0)
        if code != 0:
            raise UvUnavailableError(f"uv --version failed: {err.strip() or out.strip()}")
        return {"version": out.strip()}

    async def venv(self, path: str | Path, *, python: str | None = None) -> dict[str, Any]:
        require_python_action("uv")
        args = ["venv", str(path)]
        if python is not None:
            args += ["--python", python]
        code, _, err = await self._run(args)
        self._metrics.increment("python.uv.venv")
        return {"path": str(path), "ok": code == 0, "error": err.strip() if code else ""}

    async def pip_install(
        self, project_dir: str | Path, package: str | None = None
    ) -> dict[str, Any]:
        require_python_action("uv")
        args = ["pip", "install"]
        if package is not None:
            args.append(package)
        code, _, err = await self._run(args, cwd=project_dir)
        self._metrics.increment("python.uv.pip")
        return {
            "project": str(project_dir),
            "ok": code == 0,
            "error": err.strip() if code else "",
        }

    async def sync(self, project_dir: str | Path) -> dict[str, Any]:
        require_python_action("uv")
        code, _, err = await self._run(["sync"], cwd=project_dir)
        self._metrics.increment("python.uv.sync")
        return {
            "project": str(project_dir),
            "ok": code == 0,
            "error": err.strip() if code else "",
        }


__all__ = ["UvManager", "UvUnavailableError"]
