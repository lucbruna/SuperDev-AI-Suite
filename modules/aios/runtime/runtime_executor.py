"""Runtime executor — runs session tasks with state transitions and ACL."""
from __future__ import annotations
import asyncio
from time import monotonic
from typing import Any, Awaitable, Callable

from modules.aios.runtime.runtime_metrics import get_runtime_metrics
from modules.aios.runtime.runtime_session import RuntimeSession

TaskFn = Callable[..., Any]


class RuntimeExecutor:
    """Executes a callable inside a session, driving its state machine."""

    def __init__(self, metrics: Any | None = None) -> None:
        self._metrics = metrics or get_runtime_metrics()

    async def run(
        self,
        session: RuntimeSession,
        fn: TaskFn,
        *args: Any,
        **kwargs: Any,
    ) -> RuntimeSession:
        """Run ``fn`` within ``session``; always leaves the session terminal."""
        if session.state.value != "pending":
            raise ValueError(f"cannot run session in state {session.state.value}")

        self._metrics.session_started()
        started = monotonic()
        await session.start()

        try:
            result = fn(*args, **kwargs)
            if asyncio.iscoroutine(result) or isinstance(result, Awaitable):
                result = await result
            await session.succeed(result)
            self._metrics.session_finished(ok=True)
        except asyncio.CancelledError:
            await session.cancel()
            self._metrics.session_finished(ok=False)
            raise
        except Exception as e:  # noqa: BLE001 — runtime must always settle state
            await session.fail(e)
            self._metrics.session_finished(ok=False)
        finally:
            self._metrics.record_duration(monotonic() - started)

        return session


_runtime_executor: RuntimeExecutor | None = None


def get_runtime_executor() -> RuntimeExecutor:
    global _runtime_executor
    if _runtime_executor is None:
        _runtime_executor = RuntimeExecutor()
    return _runtime_executor


__all__ = ["RuntimeExecutor", "TaskFn", "get_runtime_executor"]
