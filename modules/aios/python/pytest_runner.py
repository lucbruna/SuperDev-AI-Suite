"""Python pytest runner — execute test suites and summarize results."""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.python.venv_manager import require_python_action

_SUMMARY_RE = re.compile(r"(\d+) (passed|failed|error|skipped)", re.IGNORECASE)


class PytestRunner:
    """Runs ``python -m pytest`` and summarizes the outcome."""

    def __init__(self, python: str | None = None) -> None:
        self.python = python or sys.executable
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(
        self, args: list[str], *, cwd: str | Path | None = None, timeout_s: float = 600.0
    ) -> tuple[int, str, str]:
        proc = await asyncio.create_subprocess_exec(
            self.python,
            "-m",
            "pytest",
            *args,
            cwd=str(cwd) if cwd else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise RuntimeError(f"pytest timed out after {timeout_s}s") from None
        return (
            int(proc.returncode or 0),
            out_b.decode("utf-8", errors="replace"),
            err_b.decode("utf-8", errors="replace"),
        )

    async def run(
        self,
        paths: list[str | Path] | None = None,
        *,
        args: list[str] | None = None,
        cwd: str | Path | None = None,
        quiet: bool = True,
    ) -> dict[str, Any]:
        require_python_action("pytest")
        cmd: list[str] = []
        if quiet:
            cmd.append("-q")
        if paths:
            cmd += [str(p) for p in paths]
        if args:
            cmd += args
        code, out, err = await self._run(cmd, cwd=cwd)
        text = out + err
        counts: dict[str, int] = {}
        for amount, label in _SUMMARY_RE.findall(text):
            counts[label.lower()] = counts.get(label.lower(), 0) + int(amount)
        self._metrics.increment("python.pytest.run")
        self._logger.log("python", "pytest run", payload={"ok": code == 0, "counts": counts})
        return {
            "ok": code == 0,
            "returncode": code,
            "passed": counts.get("passed", 0),
            "failed": counts.get("failed", 0),
            "errors": counts.get("error", 0),
            "skipped": counts.get("skipped", 0),
            "output_tail": text[-1500:],
        }


__all__ = ["PytestRunner"]
