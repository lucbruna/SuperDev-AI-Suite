"""Node client — spawns the node CLI without SDK dependencies."""
from __future__ import annotations

import asyncio
import shutil
from time import monotonic
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    get_kernel_security,
)


class NodeUnavailableError(RuntimeError):
    """Raised when the node CLI cannot be reached."""


def require_node_action(action: str) -> None:
    """Enforce the ``node:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("node", action):
        raise KernelPermissionDeniedError("node", action)


def cli_command(binary: str, args: list[str]) -> list[str]:
    """Resolve a CLI name into a spawnable command (Windows .cmd shims).

    npm/pnpm/yarn/npx are .cmd shims on Windows and cannot be spawned
    directly by CreateProcess; route them through ``cmd /c``.
    """
    resolved = shutil.which(binary)
    if resolved and resolved.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", resolved, *args]
    return [binary, *args]


async def run_cli(
    binary: str,
    args: list[str],
    *,
    component: str,
    missing: type[RuntimeError],
    timeout_s: float = 300.0,
    cwd: str | None = None,
) -> tuple[int, str, str]:
    """Run a CLI without a shell; return (returncode, stdout, stderr)."""
    started = monotonic()
    command = cli_command(binary, args)
    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
    except FileNotFoundError as exc:
        raise missing(f"{binary} CLI not found") from exc
    try:
        out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
    except TimeoutError:
        proc.kill()
        raise missing(
            f"{binary} {' '.join(args[:3])} timed out after {timeout_s}s"
        ) from None
    stdout = out_b.decode("utf-8", errors="replace")
    stderr = err_b.decode("utf-8", errors="replace")
    get_kernel_metrics().record_timing(f"{component}.cli", monotonic() - started)
    code = int(proc.returncode or 0)
    get_kernel_logger().log(
        component, f"cli: {binary} {' '.join(args[:3])} -> {code}"
    )
    return code, stdout, stderr


class NodeClient:
    """Minimal node wrapper: version, ping and inline script execution."""

    def __init__(self, binary: str = "node") -> None:
        self.binary = binary

    async def version(self) -> dict[str, Any]:
        require_node_action("node")
        code, out, err = await run_cli(
            self.binary, ["--version"], component="node", timeout_s=30.0,
            missing=NodeUnavailableError,
        )
        if code != 0:
            raise NodeUnavailableError(
                f"node --version failed: {err.strip() or out.strip()}"
            )
        return {"version": out.strip().lstrip("v")}

    async def ping(self) -> bool:
        try:
            code, _, _ = await run_cli(
                self.binary, ["--version"], component="node", timeout_s=30.0,
                missing=NodeUnavailableError,
            )
            return code == 0
        except NodeUnavailableError:
            return False

    async def exec(self, script: str, *, cwd: str | None = None) -> dict[str, Any]:
        require_node_action("run")
        code, out, err = await run_cli(
            self.binary, ["-e", script], component="node", timeout_s=120.0,
            cwd=cwd, missing=NodeUnavailableError,
        )
        return {"ok": code == 0, "stdout": out, "stderr": err}


__all__ = [
    "NodeClient",
    "NodeUnavailableError",
    "cli_command",
    "require_node_action",
    "run_cli",
]
