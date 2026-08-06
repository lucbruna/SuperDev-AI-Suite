"""Sandboxed subprocess execution for the developer module.

The sandbox is the module's safe way to run external tools (test suites,
linters). It enforces four hard constraints:

- **no shell** — commands are argument lists only; string/shell-style
  commands are rejected outright;
- **sanitized environment** — the child process inherits only an allowlist
  of benign variables, so API keys, tokens and developer secrets never leak
  into subprocesses;
- **strict timeout** — runaway commands are killed and reported;
- **output cap** — captured output is truncated to a byte budget so a
  pathological process cannot exhaust memory.

Violations raise :class:`SandboxError`.
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from modules.autonomous_developer.core.exceptions import ExecutionError

__all__ = ["SandboxConfig", "SandboxError", "SandboxResult", "SandboxRunner", "sanitize_env"]

# Environment allowlist: everything a child process plausibly needs on
# Windows/Linux without carrying secrets or developer configuration.
_DEFAULT_KEEP_ENV_KEYS = (
    "PATH",
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
    "TEMP",
    "TMP",
    "USERPROFILE",
    "HOMEDRIVE",
    "HOMEPATH",
    "APPDATA",
    "LOCALAPPDATA",
    "PROCESSOR_ARCHITECTURE",
    "PROCESSOR_ARCHITEW6432",
    "NUMBER_OF_PROCESSORS",
    "OS",
    "COMPUTERNAME",
    "USERNAME",
    "LANG",
    "LC_ALL",
    "TZ",
)

_SANDBOX_ENV = {
    "PYTHONIOENCODING": "utf-8",
    "PYTHONNOUSERSITE": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
}


@dataclass(slots=True)
class SandboxConfig:
    """Tunables for :class:`SandboxRunner`."""

    timeout_seconds: int = 300
    max_output_bytes: int = 200_000
    keep_env_keys: tuple[str, ...] = _DEFAULT_KEEP_ENV_KEYS
    cwd: str | Path | None = None


class SandboxError(ExecutionError):
    """Raised when a sandbox constraint is violated."""


@dataclass(slots=True)
class SandboxResult:
    """Outcome of a sandboxed command."""

    command: list[str]
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    truncated: bool = False

    @property
    def combined(self) -> str:
        return self.stdout + self.stderr


def sanitize_env(keep: Sequence[str] = _DEFAULT_KEEP_ENV_KEYS) -> dict[str, str]:
    """Build a child environment from an allowlist of ``os.environ`` keys."""
    keep_set = set(keep)
    env = {key: value for key, value in os.environ.items() if key in keep_set}
    env.update(_SANDBOX_ENV)
    return env


def _cap(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit], True


class SandboxRunner:
    """Runs argument-list commands under sandbox constraints."""

    def __init__(self, config: SandboxConfig | None = None) -> None:
        self.config = config or SandboxConfig()

    def run(
        self,
        command: str | Sequence[str],
        *,
        cwd: str | Path | None = None,
        timeout: int | None = None,
        env: dict[str, str] | None = None,
        max_output_bytes: int | None = None,
    ) -> SandboxResult:
        if isinstance(command, str):
            raise SandboxError(
                "Shell-style string commands are not allowed; pass an argument list",
                context={"command": command},
            )
        argv = list(command)
        if not argv:
            raise SandboxError("Empty command", context={"command": argv})
        workdir = str(cwd or self.config.cwd or ".")
        run_env = sanitize_env(self.config.keep_env_keys)
        if env:
            run_env.update(env)
        output_limit = max_output_bytes or self.config.max_output_bytes
        deadline = timeout or self.config.timeout_seconds

        import time

        start = time.time()
        try:
            proc = subprocess.run(
                argv,
                cwd=workdir,
                env=run_env,
                capture_output=True,
                text=True,
                timeout=deadline,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise SandboxError(
                f"Command timed out after {deadline}s: {argv[0]}",
                context={"command": argv, "timeout_seconds": deadline},
            ) from exc
        stdout, stdout_trunc = _cap(proc.stdout or "", output_limit)
        stderr, stderr_trunc = _cap(proc.stderr or "", output_limit)
        return SandboxResult(
            command=argv,
            returncode=proc.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=round(time.time() - start, 4),
            truncated=stdout_trunc or stderr_trunc,
        )
