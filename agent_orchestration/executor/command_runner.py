"""Command execution with timeout (Volume 31)."""

from __future__ import annotations

import shlex
import subprocess
import time
from typing import Any


class CommandRunner:
    """Runs commands with a timeout and structured output.

    Commands run **without a shell** by default (``shell=False``), which
    prevents OS command injection (CWE-78) when the command string contains
    untrusted input. Pass ``shell=True`` explicitly only for trusted commands
    that genuinely need shell features (pipes, globbing, redirection).
    """

    def __init__(self, timeout: float = 5.0, dry_run: bool = False) -> None:
        self.timeout = timeout
        self.dry_run = dry_run

    def run(self, command: str, shell: bool = False) -> dict[str, Any]:
        started = time.monotonic()
        if self.dry_run:
            return {"ok": True, "dry_run": True, "command": command,
                    "duration": 0.0}
        try:
            if shell:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True,
                    timeout=self.timeout, check=False)
            else:
                result = subprocess.run(
                    shlex.split(command), capture_output=True, text=True,
                    timeout=self.timeout, check=False)
            duration = time.monotonic() - started
            return {"ok": result.returncode == 0,
                    "returncode": result.returncode,
                    "output": (result.stdout or "").strip(),
                    "error": (result.stderr or "").strip(),
                    "duration": duration}
        except subprocess.TimeoutExpired as exc:
            return {"ok": False, "error": f"timeout:{self.timeout}s",
                    "output": str(exc), "duration": self.timeout}
        except OSError as exc:
            return {"ok": False, "error": str(exc),
                    "duration": time.monotonic() - started}
