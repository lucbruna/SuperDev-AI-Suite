"""Runtime session — lifecycle of a single execution within the AIOS runtime."""
from __future__ import annotations
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from modules.aios.kernel.kernel_events import emit
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.runtime.runtime_context import RuntimeContext
from modules.aios.runtime.runtime_state import RuntimeState, snapshot_of, state_guard


class RuntimeSession:
    """Owns the state machine, timing and lifecycle events of one execution."""

    def __init__(self, context: RuntimeContext, session_id: str | None = None) -> None:
        self.id = session_id or uuid4().hex
        self.context = context
        self._state = RuntimeState.PENDING
        self.created_at = datetime.now(UTC).isoformat()
        self.started_at: str | None = None
        self.finished_at: str | None = None
        self.error: str | None = None
        self.result: Any = None
        self._logger = get_kernel_logger()

    @property
    def state(self) -> RuntimeState:
        return self._state

    def _transition(self, target: RuntimeState) -> None:
        state_guard(self._state, target, label=f"session {self.id}")
        self._state = target

    async def start(self) -> None:
        self._transition(RuntimeState.RUNNING)
        self.started_at = datetime.now(UTC).isoformat()
        self._logger.log("runtime", f"session {self.id} started ({self.context.name})")
        try:
            import asyncio

            asyncio.get_running_loop().create_task(
                emit("session.started", session_id=self.id, name=self.context.name)
            )
        except RuntimeError:
            pass

    async def succeed(self, result: Any = None) -> None:
        self._transition(RuntimeState.SUCCEEDED)
        self.result = result
        self.finished_at = datetime.now(UTC).isoformat()
        self._logger.log("runtime", f"session {self.id} succeeded")
        try:
            import asyncio

            asyncio.get_running_loop().create_task(
                emit("session.succeeded", session_id=self.id, name=self.context.name)
            )
        except RuntimeError:
            pass

    async def fail(self, error: Exception | str) -> None:
        self._transition(RuntimeState.FAILED)
        self.error = str(error)
        self.finished_at = datetime.now(UTC).isoformat()
        self._logger.log("runtime", f"session {self.id} failed: {self.error}", level="error")
        try:
            import asyncio

            asyncio.get_running_loop().create_task(
                emit("session.failed", session_id=self.id, name=self.context.name, error=self.error)
            )
        except RuntimeError:
            pass

    async def cancel(self) -> None:
        self._transition(RuntimeState.CANCELLED)
        self.finished_at = datetime.now(UTC).isoformat()
        self._logger.log("runtime", f"session {self.id} cancelled")
        try:
            import asyncio

            asyncio.get_running_loop().create_task(
                emit("session.cancelled", session_id=self.id, name=self.context.name)
            )
        except RuntimeError:
            pass

    def snapshot(self) -> dict[str, Any]:
        return {
            "session_id": self.id,
            **snapshot_of(self._state),
            "name": self.context.name,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
            "has_result": self.result is not None,
        }


__all__ = ["RuntimeSession"]
