"""Process runtime facade — unified API for process management."""
from __future__ import annotations

from modules.aios.process.acl import require_process_action
from modules.aios.process.process_cleanup import CleanupResult, ProcessCleanup
from modules.aios.process.process_executor import ExecutionResult, ProcessExecutor
from modules.aios.process.process_manager import ProcessError, ProcessInfo, ProcessManager
from modules.aios.process.process_monitor import ProcessMetrics, ProcessMonitor
from modules.aios.process.process_pool import PoolWorker, ProcessPool
from modules.aios.process.process_tree import ProcessNode, ProcessTree

from modules.aios import get_kernel_logger, get_kernel_metrics


class ProcessRuntime:
    """Facade over process management operations.

    The runtime is always available — no external dependency.
    """

    def __init__(self) -> None:
        self._manager = ProcessManager()
        self._pool = ProcessPool()
        self._executor = ProcessExecutor()
        self._monitor = ProcessMonitor()
        self._tree = ProcessTree()
        self._cleanup = ProcessCleanup()
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    @property
    def manager(self) -> ProcessManager:
        return self._manager

    @property
    def pool(self) -> ProcessPool:
        return self._pool

    @property
    def executor(self) -> ProcessExecutor:
        return self._executor

    @property
    def monitor(self) -> ProcessMonitor:
        return self._monitor

    @property
    def tree(self) -> ProcessTree:
        return self._tree

    @property
    def cleanup(self) -> ProcessCleanup:
        return self._cleanup

    def available(self) -> bool:
        """Process runtime is always available."""
        return True

    async def snapshot(self) -> dict:
        """Best-effort inventory of process state."""
        return {
            "available": True,
            "managed_processes": len(self._manager.list()),
            "pool_workers": len(self._pool._workers),
            "pool_running": self._pool._running,
            "monitor_active": self._monitor._monitoring,
        }

    async def close(self) -> None:
        """No-op — process runtime is stateless."""
        await self._pool.shutdown()
        await self._monitor.stop()


_process_runtime: ProcessRuntime | None = None


def get_process_runtime() -> ProcessRuntime:
    """Singleton accessor for the process runtime."""
    global _process_runtime
    if _process_runtime is None:
        _process_runtime = ProcessRuntime()
    return _process_runtime


__all__ = [
    "ProcessRuntime",
    "get_process_runtime",
    "require_process_action",
    "ProcessManager",
    "ProcessInfo",
    "ProcessError",
    "ProcessPool",
    "PoolWorker",
    "ProcessExecutor",
    "ExecutionResult",
    "ProcessMonitor",
    "ProcessMetrics",
    "ProcessTree",
    "ProcessNode",
    "ProcessCleanup",
    "CleanupResult",
]
