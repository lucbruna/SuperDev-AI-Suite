"""Process package — process management with kernel ACL (Vol 12, Fase 27)."""
from __future__ import annotations

from modules.aios.process.acl import require_process_action
from modules.aios.process.process import (
    CleanupResult,
    ExecutionResult,
    PoolWorker,
    ProcessCleanup,
    ProcessExecutor,
    ProcessInfo,
    ProcessManager,
    ProcessMetrics,
    ProcessMonitor,
    ProcessNode,
    ProcessPool,
    ProcessRuntime,
    ProcessTree,
    get_process_runtime,
)
from modules.aios.process.process_cleanup import CleanupResult as _CleanupResult
from modules.aios.process.process_executor import ExecutionResult as _ExecutionResult
from modules.aios.process.process_manager import ProcessError, ProcessInfo as _ProcessInfo, ProcessManager as _ProcessManager
from modules.aios.process.process_monitor import ProcessMetrics as _ProcessMetrics, ProcessMonitor as _ProcessMonitor
from modules.aios.process.process_pool import PoolWorker as _PoolWorker, ProcessPool as _ProcessPool
from modules.aios.process.process_tree import ProcessNode as _ProcessNode, ProcessTree as _ProcessTree

__all__ = [
    "CleanupResult",
    "ExecutionResult",
    "PoolWorker",
    "ProcessCleanup",
    "ProcessError",
    "ProcessExecutor",
    "ProcessInfo",
    "ProcessManager",
    "ProcessMetrics",
    "ProcessMonitor",
    "ProcessNode",
    "ProcessPool",
    "ProcessRuntime",
    "ProcessTree",
    "get_process_runtime",
    "require_process_action",
]
