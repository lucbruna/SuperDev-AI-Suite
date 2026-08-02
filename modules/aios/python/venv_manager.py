"""Python venv manager — create, inspect and remove virtual environments."""
from __future__ import annotations

import asyncio
import shutil
import sys
from pathlib import Path
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    get_kernel_security,
)


class VenvError(RuntimeError):
    """Raised when a virtual environment operation fails."""


def require_python_action(action: str) -> None:
    """Enforce the ``python:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("python", action):
        raise KernelPermissionDeniedError("python", action)


class VenvManager:
    """Creates/removes virtual environments with the system interpreter."""

    def __init__(self, python: str | None = None) -> None:
        self.python = python or sys.executable
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(self, args: list[str], *, timeout_s: float = 300.0) -> tuple[int, str, str]:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise VenvError(f"venv command timed out after {timeout_s}s") from None
        return (
            int(proc.returncode or 0),
            out_b.decode("utf-8", errors="replace"),
            err_b.decode("utf-8", errors="replace"),
        )

    @staticmethod
    def python_bin(venv_path: str | Path) -> str:
        """Path to the venv's interpreter (Scripts on Windows, bin elsewhere)."""
        root = Path(venv_path)
        candidate = root / "Scripts" / "python.exe" if sys.platform == "win32" else root / "bin" / "python"
        return str(candidate)

    async def create(
        self, path: str | Path, *, system_site_packages: bool = False
    ) -> dict[str, Any]:
        require_python_action("venv")
        args = [self.python, "-m", "venv"]
        if system_site_packages:
            args.append("--system-site-packages")
        args.append(str(path))
        code, out, err = await self._run(args)
        self._metrics.increment("python.venv.create")
        self._logger.log("python", f"venv create {path}", payload={"ok": code == 0})
        return {
            "path": str(path),
            "ok": code == 0,
            "python": self.python_bin(path) if code == 0 else "",
            "error": err.strip() if code else "",
        }

    async def remove(self, path: str | Path) -> dict[str, Any]:
        require_python_action("venv")
        root = Path(path)
        if not root.exists():
            return {"path": str(path), "ok": True, "removed": False}
        try:
            shutil.rmtree(root)
            removed = True
        except OSError as exc:
            return {"path": str(path), "ok": False, "error": str(exc)}
        self._metrics.increment("python.venv.remove")
        return {"path": str(path), "ok": True, "removed": removed}

    async def exists(self, path: str | Path) -> bool:
        return Path(self.python_bin(path)).exists()


__all__ = ["VenvManager", "VenvError", "require_python_action"]
