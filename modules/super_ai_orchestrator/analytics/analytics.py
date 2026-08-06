"""OrchestratorAnalytics — deterministic execution analytics.

Computes distributions and rates over the tasks currently known to the
kernel. Pure function of kernel state: the same tasks produce the same
analytics every time.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from modules.super_ai_orchestrator.core.status import TaskStatus
from modules.super_ai_orchestrator.kernel import OrchestrationKernel


class OrchestratorAnalytics:
    """Analyses kernel tasks: throughput, owners, kinds, quality."""

    def analyze(self, kernel: OrchestrationKernel) -> dict[str, Any]:
        tasks = kernel.tasks()
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        failed = [t for t in tasks if t.status == TaskStatus.FAILED]
        rolled_back = [t for t in tasks if t.status == TaskStatus.ROLLED_BACK]
        cancelled = [t for t in tasks if t.status == TaskStatus.CANCELLED]

        finished = completed + failed
        success_rate = round(len(completed) / len(finished), 4) if finished else 1.0
        avg_attempts = (
            round(sum(t.attempts for t in finished) / len(finished), 4)
            if finished
            else 0.0
        )
        rollback_rate = (
            round(len(rolled_back) / len(failed), 4) if failed else 0.0
        )

        return {
            "totals": {
                "tasks": len(tasks),
                "completed": len(completed),
                "failed": len(failed),
                "cancelled": len(cancelled),
                "rolled_back": len(rolled_back),
                "success_rate": success_rate,
                "avg_attempts": avg_attempts,
                "rollback_rate": rollback_rate,
            },
            "by_kind": dict(Counter(t.kind for t in finished)),
            "by_owner": dict(
                Counter(t.owner or "unassigned" for t in finished)
            ),
            "by_llm": dict(Counter(t.llm or "none" for t in finished)),
            "top_failures": [
                {"title": t.title, "kind": t.kind, "error": t.error}
                for t in sorted(failed, key=lambda t: t.seq)
            ],
        }

    def report(self, kernel: OrchestrationKernel) -> str:
        """Compact multi-line analytics summary."""
        a = self.analyze(kernel)
        t = a["totals"]
        lines = [
            f"tasks={t['tasks']} completed={t['completed']} "
            f"failed={t['failed']} success_rate={t['success_rate']}",
            f"by_kind: {a['by_kind'] or '(none)'}",
            f"by_owner: {a['by_owner'] or '(none)'}",
            f"by_llm: {a['by_llm'] or '(none)'}",
        ]
        return "\n".join(lines)
