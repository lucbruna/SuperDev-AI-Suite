"""Workload Distribution — round-robin job assignment across workers."""
from __future__ import annotations

from typing import Any


class WorkloadDistribution:
    """Assigns jobs to workers evenly (round-robin)."""

    def plan(self, jobs: list[str], workers: list[str]) -> dict[str, Any]:
        if not workers:
            return {"ok": False, "error": "no workers available", "assignments": []}
        assignments = [
            {"job": job, "worker": workers[i % len(workers)]}
            for i, job in enumerate(jobs)
        ]
        per_worker = {w: sum(1 for a in assignments if a["worker"] == w) for w in workers}
        return {"assignments": assignments, "per_worker": per_worker}


_workload_distribution: WorkloadDistribution | None = None


def get_workload_distribution() -> WorkloadDistribution:
    global _workload_distribution
    if _workload_distribution is None:
        _workload_distribution = WorkloadDistribution()
    return _workload_distribution
