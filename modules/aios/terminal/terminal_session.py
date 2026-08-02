"""Terminal session — a named shell session with state and output stream."""
from __future__ import annotations

import asyncio
import shutil
import sys
from pathlib import Path
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.terminal.terminal_stream import TerminalStream


class TerminalSessionError(RuntimeError):
    """Raised when a terminal session cannot start or run."""


def _default_shell() -> str:
    return "powershell" if sys.platform == "win32" else "bash"


class TerminalSession:
    """Runs commands inside a named shell context (cwd + shell).

    Each ``run`` spawns a fresh subprocess against the session's working
    directory so execution is deterministic; output is accumulated into a
    bounded TerminalStream.
    """

    def __init__(
        self,
        name: str,
        *,
        shell: str | None = None,
        cwd: str | None = None,
    ) -> None:
        self.name = name
        self.shell = shell or _default_shell()
        self.cwd = cwd or str(Path.cwd())
        self.stream = TerminalStream()
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    async def start(self) -> bool:
        """Verify the shell binary is reachable."""
        if shutil.which(self.shell) is None:
            raise TerminalSessionError(f"shell not found: {self.shell}")
        self._closed = False
        return True

    async def run(
        self, command: str, *, timeout_s: float = 120.0
    ) -> dict[str, Any]:
        if self._closed:
            raise TerminalSessionError(f"session '{self.name}' is closed")
        args = (
            [self.shell, "-NoProfile", "-Command", command]
            if self.shell.lower() == "powershell"
            else [self.shell, "-c", command]
        )
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
            )
        except (FileNotFoundError, OSError) as exc:
            raise TerminalSessionError(f"cannot run {self.shell}: {exc}") from exc
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise TerminalSessionError(
                f"command timed out after {timeout_s}s"
            ) from None
        stdout = out_b.decode("utf-8", errors="replace")
        stderr = err_b.decode("utf-8", errors="replace")
        self.stream.write(stdout + (f"\n{stderr}" if stderr else ""))
        code = int(proc.returncode or 0)
        self._metrics.increment("terminal.run")
        self._logger.log(
            "terminal", f"session {self.name}: {command[:40]!r} -> {code}"
        )
        return {"ok": code == 0, "stdout": stdout.strip(), "stderr": stderr.strip()}

    async def close(self) -> None:
        self._closed = True


__all__ = ["TerminalSession", "TerminalSessionError", "TerminalStream"]
