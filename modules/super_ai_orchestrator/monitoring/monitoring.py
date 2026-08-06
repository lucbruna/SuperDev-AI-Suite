"""OrchestratorMonitor — deterministic health assessment.

Computes a health verdict and a flat metric surface from the kernel state.
Pure function of the kernel: no clock, no I/O. The verdict is
``healthy`` / ``degraded`` / ``error`` based on observable conditions.
"""
from __future__ import annotations

from typing import Any

from modules.super_ai_orchestrator.core.status import TaskStatus
from modules.super_ai_orchestrator.kernel import OrchestrationKernel


class OrchestratorMonitor:
    """Reads kernel state and produces health/metrics snapshots."""

    def health(self, kernel: OrchestrationKernel) -> dict[str, Any]:
        """Assess orchestrator health."""
        stats = kernel.stats()
        issues: list[str] = []
        status = "healthy"

        if kernel.executor is None:
            issues.append("no executor registered: tasks cannot run")
            status = "degraded"

        waiting = kernel.by_status(TaskStatus.WAITING_APPROVAL)
        if waiting:
            issues.append(f"{len(waiting)} task(s) waiting for approval")
            status = "degraded"

        if stats["running"] > kernel.config.max_concurrent:
            issues.append(
                f"running ({stats['running']}) exceeds max_concurrent "
                f"({kernel.config.max_concurrent})"
            )
            status = "error"

        return {
            "status": status,
            "issues": issues,
            "metrics": self.metrics(kernel),
        }

    def metrics(self, kernel: OrchestrationKernel) -> dict[str, Any]:
        """A flat, deterministic metric surface for the orchestrator."""
        stats = kernel.stats()
        counts = stats["counts"]
        completed = counts[TaskStatus.COMPLETED.value]
        failed = counts[TaskStatus.FAILED.value]
        total_finished = completed + failed
        success_rate = (
            round(completed / total_finished, 4) if total_finished else 1.0
        )
        return {
            "total": stats["total"],
            "running": stats["running"],
            "queued": stats["queued"],
            "waiting_approval": stats["waiting_approval"],
            "completed": completed,
            "failed": failed,
            "cancelled": counts[TaskStatus.CANCELLED.value],
            "paused": counts[TaskStatus.PAUSED.value],
            "rolled_back": counts[TaskStatus.ROLLED_BACK.value],
            "success_rate": success_rate,
            "audit_records": len(kernel.audit.records),
            "event_records": len(kernel.event_bus.log),
        }

    def summary(self, kernel: OrchestrationKernel) -> str:
        """One-line deterministic summary for logs and CLIs."""
        m = self.metrics(kernel)
        return (
            f"orchestrator: total={m['total']} running={m['running']} "
            f"queued={m['queued']} completed={m['completed']} "
            f"failed={m['failed']} success_rate={m['success_rate']}"
        )
