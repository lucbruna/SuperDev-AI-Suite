"""Kubernetes client — low-level wrapper around the kubectl CLI."""
from __future__ import annotations

import asyncio
import json
from time import monotonic
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    get_kernel_security,
)


class KubernetesUnavailableError(RuntimeError):
    """Raised when the kubectl CLI or cluster cannot be reached."""


def require_kubernetes_action(action: str) -> None:
    """Enforce the ``kubernetes:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("kubernetes", action):
        raise KernelPermissionDeniedError("kubernetes", action)


class KubernetesClient:
    """Spawns the ``kubectl`` CLI as a subprocess (no SDK dependency)."""

    def __init__(self, binary: str = "kubectl") -> None:
        self.binary = binary
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(
        self, args: list[str], *, timeout_s: float | None = 120.0
    ) -> tuple[int, str, str]:
        """Run the CLI without a shell; return (returncode, stdout, stderr)."""
        started = monotonic()
        try:
            proc = await asyncio.create_subprocess_exec(
                self.binary,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise KubernetesUnavailableError(
                f"kubectl CLI not found: {self.binary}"
            ) from exc
        try:
            stdout_b, stderr_b = await asyncio.wait_for(
                proc.communicate(), timeout=timeout_s
            )
        except TimeoutError:
            proc.kill()
            raise KubernetesUnavailableError(
                f"kubectl {' '.join(args[:3])} timed out after {timeout_s}s"
            ) from None
        stdout = stdout_b.decode("utf-8", errors="replace")
        stderr = stderr_b.decode("utf-8", errors="replace")
        self._metrics.record_timing("kubernetes.cli", monotonic() - started)
        returncode = int(proc.returncode or 0)
        self._logger.log(
            "kubernetes", f"cli: kubectl {' '.join(args[:3])} -> {returncode}"
        )
        return returncode, stdout, stderr

    @staticmethod
    def first_json(text: str) -> dict[str, Any]:
        """Parse the first JSON object in kubectl ``-o json`` output."""
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
        raise ValueError(f"no JSON object in kubectl output: {text[:200]!r}")

    async def version(self) -> dict[str, Any]:
        require_kubernetes_action("cluster")
        code, out, err = await self._run(["version", "-o", "json"], timeout_s=30.0)
        if code != 0:
            raise KubernetesUnavailableError(
                f"kubectl version failed: {err.strip() or out.strip()}"
            )
        return self.first_json(out)

    async def ping(self) -> bool:
        """True when a cluster context is configured and reachable."""
        try:
            code, _, _ = await self._run(["cluster-info"], timeout_s=30.0)
            return code == 0
        except KubernetesUnavailableError:
            return False


__all__ = [
    "KubernetesClient",
    "KubernetesUnavailableError",
    "require_kubernetes_action",
]
