"""Java client — compiles and runs Java sources with the JDK toolchain."""
from __future__ import annotations

import asyncio
from time import monotonic
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    get_kernel_security,
)


class JavaUnavailableError(RuntimeError):
    """Raised when the JDK (java/javac) cannot be reached."""


def require_java_action(action: str) -> None:
    """Enforce the ``java:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("java", action):
        raise KernelPermissionDeniedError("java", action)


class JavaClient:
    """Spawns ``java``/``javac`` as subprocesses (no SDK dependency)."""

    def __init__(self, java: str = "java", javac: str = "javac") -> None:
        self.java = java
        self.javac = javac
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(
        self, binary: str, args: list[str], *, timeout_s: float = 120.0
    ) -> tuple[int, str, str]:
        started = monotonic()
        try:
            proc = await asyncio.create_subprocess_exec(
                binary,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise JavaUnavailableError(f"{binary} CLI not found") from exc
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise JavaUnavailableError(
                f"{binary} {' '.join(args[:3])} timed out after {timeout_s}s"
            ) from None
        stdout = out_b.decode("utf-8", errors="replace")
        stderr = err_b.decode("utf-8", errors="replace")
        self._metrics.record_timing("java.cli", monotonic() - started)
        code = int(proc.returncode or 0)
        self._logger.log("java", f"cli: {binary} {' '.join(args[:3])} -> {code}")
        return code, stdout, stderr

    async def version(self) -> dict[str, Any]:
        require_java_action("inspect")
        code, out, err = await self._run(self.java, ["-version"], timeout_s=30.0)
        if code != 0:
            raise JavaUnavailableError(f"java -version failed: {err.strip() or out.strip()}")
        # java -version prints to stderr on OpenJDK
        text = (out or err).strip().splitlines()
        return {"version": text[0] if text else ""}

    async def ping(self) -> bool:
        try:
            code, _, _ = await self._run(self.java, ["-version"], timeout_s=30.0)
            return code == 0
        except JavaUnavailableError:
            return False

    async def compile(
        self, sources: list[str], *, output: str, classpath: str | None = None
    ) -> dict[str, Any]:
        require_java_action("compile")
        args = ["-d", output]
        if classpath:
            args += ["-cp", classpath]
        args += sources
        code, out, err = await self._run(self.javac, args)
        self._metrics.increment("java.compile")
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def run(
        self, main_class: str, *, classpath: str | None = None, args: list[str] | None = None
    ) -> dict[str, Any]:
        require_java_action("run")
        run_args = ["-cp", classpath or "."]
        run_args += [main_class]
        if args:
            run_args += args
        code, out, err = await self._run(self.java, run_args)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["JavaClient", "JavaUnavailableError", "require_java_action"]
