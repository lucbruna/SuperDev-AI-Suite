"""Runtime cleanup — best-effort teardown of per-session artifacts."""
from __future__ import annotations
from typing import Any, Callable

from modules.aios.kernel.kernel_logger import get_kernel_logger

CleanupFn = Callable[[], None]


class RuntimeCleanup:
    """Registers and runs per-session cleanup callbacks (never raises)."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._cleanup: dict[str, list[CleanupFn]] = {}

    def register(self, session_id: str, fn: CleanupFn) -> None:
        self._cleanup.setdefault(session_id, []).append(fn)

    def run(self, session_id: str) -> int:
        """Run all cleanup callbacks for a session; return failures count."""
        failures = 0
        for fn in self._cleanup.pop(session_id, []):
            try:
                fn()
            except Exception as e:  # noqa: BLE001 — cleanup must never break teardown
                failures += 1
                self._logger.log(
                    "runtime",
                    f"cleanup failed for session {session_id}: {e}",
                    level="warning",
                )
        return failures

    def snapshot(self) -> dict[str, Any]:
        return {
            "pending_sessions": len(self._cleanup),
            "pending_callbacks": sum(len(v) for v in self._cleanup.values()),
        }


_runtime_cleanup: RuntimeCleanup | None = None


def get_runtime_cleanup() -> RuntimeCleanup:
    global _runtime_cleanup
    if _runtime_cleanup is None:
        _runtime_cleanup = RuntimeCleanup()
    return _runtime_cleanup


__all__ = ["RuntimeCleanup", "CleanupFn", "get_runtime_cleanup"]
