"""Command execution with dry runs, deny patterns and timeouts."""
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from modules.autonomous_developer.core.exceptions import ExecutionError

__all__ = ["CommandResult", "CommandRunner"]

_DEFAULT_DENY_PATTERNS = ("rm -rf", "del /s", "format ", "shutdown")


@dataclass(slots=True)
class CommandResult:
    """Outcome of a command execution."""

    command: str
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    dry_run: bool = False


class CommandRunner:
    """Runs shell commands under deny-pattern and timeout constraints.

    Dry runs never touch the shell; they return a deterministic result. A
    command matching a deny pattern raises :class:`ExecutionError` in both
    modes so dry runs surface exactly what a real run would reject.
    """

    def __init__(
        self,
        deny_patterns: tuple[str, ...] | list[str] | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        self.deny_patterns = tuple(deny_patterns or _DEFAULT_DENY_PATTERNS)
        self.timeout_seconds = timeout_seconds

    def violations(self, command: str) -> list[str]:
        """Deny patterns present in ``command`` (case-insensitive)."""
        lowered = command.lower()
        return [pattern for pattern in self.deny_patterns if pattern.lower() in lowered]

    def run(
        self,
        command: str,
        *,
        cwd: str | Path | None = None,
        timeout: int | None = None,
        dry_run: bool = False,
    ) -> CommandResult:
        blocked = self.violations(command)
        if blocked:
            raise ExecutionError(
                f"Command blocked: {', '.join(blocked)}",
                context={"command": command},
            )
        if dry_run:
            return CommandResult(
                command=command, returncode=0, stdout=f"DRY-RUN: {command}", dry_run=True
            )
        start = time.time()
        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(cwd) if cwd is not None else None,
                timeout=timeout or self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise ExecutionError(
                f"Command timed out: {command}", context={"command": command}
            ) from exc
        return CommandResult(
            command=command,
            returncode=proc.returncode,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            duration_seconds=round(time.time() - start, 4),
        )
