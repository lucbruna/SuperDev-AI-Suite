"""Sandbox limits — time/memory/storage budgets enforced by the sandbox."""
from __future__ import annotations
from typing import Any


class SandboxLimitError(Exception):
    def __init__(self, resource: str, message: str) -> None:
        self.resource = resource
        super().__init__(f"sandbox limit exceeded ({resource}): {message}")


class SandboxLimits:
    """Tracks consumption against the policy's resource budgets."""

    def __init__(
        self,
        *,
        timeout_s: float | None = None,
        max_memory_mb: int | None = None,
        max_storage_mb: int | None = None,
    ) -> None:
        self.timeout_s = timeout_s
        self.max_memory_mb = max_memory_mb
        self.max_storage_mb = max_storage_mb
        self._used_storage_mb = 0.0
        self._elapsed_s = 0.0

    def record_storage(self, bytes_: int) -> None:
        self._used_storage_mb += bytes_ / (1024 * 1024)
        if self.max_storage_mb is not None and self._used_storage_mb > self.max_storage_mb:
            raise SandboxLimitError(
                "storage",
                f"{self._used_storage_mb:.1f}MB > {self.max_storage_mb}MB",
            )

    def check_timeout(self, elapsed_s: float) -> None:
        self._elapsed_s = elapsed_s
        if self.timeout_s is not None and elapsed_s > self.timeout_s:
            raise SandboxLimitError("timeout", f"{elapsed_s:.2f}s > {self.timeout_s}s")

    def record_elapsed(self, elapsed_s: float) -> None:
        """Record elapsed time without enforcing the budget.

        Used for accounting after a run that already completed (the timeout
        itself is enforced during execution via asyncio.wait_for) — a
        successful run must never fail in teardown for going slightly over.
        """
        self._elapsed_s = elapsed_s

    def check_memory(self, used_mb: float) -> None:
        if self.max_memory_mb is not None and used_mb > self.max_memory_mb:
            raise SandboxLimitError("memory", f"{used_mb:.1f}MB > {self.max_memory_mb}MB")

    def snapshot(self) -> dict[str, Any]:
        return {
            "timeout_s": self.timeout_s,
            "max_memory_mb": self.max_memory_mb,
            "max_storage_mb": self.max_storage_mb,
            "used_storage_mb": round(self._used_storage_mb, 3),
            "elapsed_s": round(self._elapsed_s, 3),
        }


__all__ = ["SandboxLimitError", "SandboxLimits"]
