"""Runtime engine — facade composing sessions, executor, metrics and cleanup."""
from __future__ import annotations
from typing import Any

from modules.aios.runtime.runtime_cleanup import RuntimeCleanup, get_runtime_cleanup
from modules.aios.runtime.runtime_context import RuntimeContext
from modules.aios.runtime.runtime_executor import RuntimeExecutor, TaskFn, get_runtime_executor
from modules.aios.runtime.runtime_metrics import RuntimeMetrics, get_runtime_metrics
from modules.aios.runtime.runtime_session import RuntimeSession
from modules.aios.runtime.runtime_state import RuntimeState


class RuntimeEngine:
    """Owns sessions created in this process and runs their tasks."""

    def __init__(
        self,
        executor: RuntimeExecutor | None = None,
        cleanup: RuntimeCleanup | None = None,
        metrics: RuntimeMetrics | None = None,
    ) -> None:
        self.executor = executor or get_runtime_executor()
        self.cleanup = cleanup or get_runtime_cleanup()
        self.metrics = metrics or get_runtime_metrics()
        self._sessions: dict[str, RuntimeSession] = {}

    def create_session(self, name: str, **kwargs: Any) -> RuntimeSession:
        """Create a pending session from a context (env/cwd/inputs/timeout...)."""
        session = RuntimeSession(RuntimeContext(name=name, **kwargs))
        self._sessions[session.id] = session
        self.metrics.active_sessions(len(self._sessions))
        return session

    def get(self, session_id: str) -> RuntimeSession | None:
        return self._sessions.get(session_id)

    async def run(self, name: str, fn: TaskFn, *args: Any, **kwargs: Any) -> RuntimeSession:
        """Create a session, run ``fn`` and return the terminal session."""
        session = self.create_session(name)
        return await self.run_session(session, fn, *args, **kwargs)

    async def run_session(
        self,
        session: RuntimeSession,
        fn: TaskFn,
        *args: Any,
        **kwargs: Any,
    ) -> RuntimeSession:
        try:
            return await self.executor.run(session, fn, *args, **kwargs)
        finally:
            self.metrics.active_sessions(len(self._sessions))

    def close(self, session_id: str) -> dict[str, Any]:
        """Run cleanup for a session and drop it from the engine registry."""
        session = self._sessions.pop(session_id, None)
        failures = self.cleanup.run(session_id)
        self.metrics.active_sessions(len(self._sessions))
        return {
            "session_id": session_id,
            "closed": session is not None,
            "cleanup_failures": failures,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "sessions": {
                session.id: {
                    "name": session.context.name,
                    "state": session.state.value,
                }
                for session in self._sessions.values()
            },
            "counts": {
                "total": len(self._sessions),
                "running": sum(1 for s in self._sessions.values() if s.state == RuntimeState.RUNNING),
                "terminal": sum(1 for s in self._sessions.values() if s.state in RuntimeState.terminal()),
            },
            "cleanup": self.cleanup.snapshot(),
        }


_runtime_engine: RuntimeEngine | None = None


def get_runtime_engine() -> RuntimeEngine:
    global _runtime_engine
    if _runtime_engine is None:
        _runtime_engine = RuntimeEngine()
    return _runtime_engine


__all__ = ["RuntimeEngine", "RuntimeSession", "get_runtime_engine"]
