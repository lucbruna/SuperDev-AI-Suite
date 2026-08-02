"""Python pip manager — install, uninstall and list packages."""
from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.python.venv_manager import require_python_action


class PipManager:
    """Package lifecycle via ``python -m pip``."""

    def __init__(self, python: str | None = None) -> None:
        self.python = python or sys.executable
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(self, args: list[str], *, timeout_s: float = 300.0) -> tuple[int, str, str]:
        proc = await asyncio.create_subprocess_exec(
            self.python,
            "-m",
            "pip",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise RuntimeError(f"pip timed out after {timeout_s}s") from None
        return (
            int(proc.returncode or 0),
            out_b.decode("utf-8", errors="replace"),
            err_b.decode("utf-8", errors="replace"),
        )

    async def install(self, package: str, *, upgrade: bool = False) -> dict[str, Any]:
        require_python_action("pip")
        args = ["install"]
        if upgrade:
            args.append("--upgrade")
        args.append(package)
        code, _, err = await self._run(args)
        self._metrics.increment("python.pip.install")
        self._logger.log("python", f"pip install {package}", payload={"ok": code == 0})
        return {"package": package, "ok": code == 0, "error": err.strip() if code else ""}

    async def uninstall(self, package: str) -> dict[str, Any]:
        require_python_action("pip")
        code, _, err = await self._run(["uninstall", "-y", package])
        self._metrics.increment("python.pip.uninstall")
        return {"package": package, "ok": code == 0, "error": err.strip() if code else ""}

    async def list(self) -> list[dict[str, Any]]:
        require_python_action("pip")
        code, out, err = await self._run(["list", "--format=json"])
        if code != 0:
            raise RuntimeError(f"pip list failed: {err.strip() or out.strip()}")
        self._metrics.increment("python.pip.list")
        return json.loads(out) if out.strip() else []

    async def freeze(self) -> list[str]:
        require_python_action("pip")
        code, out, err = await self._run(["freeze"])
        if code != 0:
            raise RuntimeError(f"pip freeze failed: {err.strip() or out.strip()}")
        return [line for line in out.splitlines() if line.strip()]


__all__ = ["PipManager"]
