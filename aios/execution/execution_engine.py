"""ExecutionEngine: facade that runs plans/jobs with retries, rollback and checkpoints."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from aios.execution.agent_dispatcher import AgentDispatcher
from aios.execution.checkpoint_manager import CheckpointManager
from aios.execution.distributed_executor import DistributedExecutor
from aios.execution.job_dispatcher import Job, JobDispatcher
from aios.execution.parallel_executor import ParallelExecutor
from aios.execution.retry_policy import RetryPolicy
from aios.execution.rollback_manager import RollbackManager
from aios.planning.task_builder import Task
from aios.planning.workflow_planner import WorkflowPlan

EXECUTION_MODES = ("sequential", "parallel")
EXECUTION_STATUSES = ("idle", "running", "completed", "failed", "cancelled")


@dataclass
class Execution:
    execution_id: str
    status: str = "idle"
    jobs: dict[str, Job] = field(default_factory=dict)
    completed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class ExecutionEngine:
    """Executes task functions honoring the workflow dependency order."""

    def __init__(self, engine_id: str | None = None, retry_policy: RetryPolicy | None = None) -> None:
        self.engine_id = engine_id or f"engine-{uuid.uuid4().hex[:8]}"
        self.jobs = JobDispatcher()
        self.agents = AgentDispatcher()
        self.parallel = ParallelExecutor()
        self.distributed = DistributedExecutor()
        self.retry = retry_policy or RetryPolicy(max_attempts=3, backoff="exponential", base_delay=0.1, max_delay=5.0)
        self.rollback = RollbackManager()
        self.checkpoints = CheckpointManager()
        self._executions: dict[str, Execution] = {}

    # -- primitives ---------------------------------------------------------

    def submit_task(self, task_id: str, name: str, params: dict[str, Any] | None = None, agent: str | None = None) -> Job:
        task = Task(task_id=task_id, name=name, params=dict(params or {}), agent=agent)
        return self.jobs.submit(task=task, agent=agent)

    def run_job(self, job_id: str, fn: Callable[[Task], Any]) -> Any:
        job = self.jobs.get(job_id)
        if job is None:
            raise KeyError(f"unknown job {job_id!r}")
        task = Task(task_id=job.task_id, name=job.name, params=dict(job.params), agent=job.agent)
        result = self._run_task(task, fn, agent=job.agent)
        job.result = result
        job.status = "completed"
        return result

    def execute_task(self, task: Task, fn: Callable[[Task], Any] | None = None, agent: str | None = None) -> Any:
        fn = fn if fn is not None else (lambda t: t.params)
        return self._run_task(task, fn, agent=agent)

    def _run_task(self, task: Task, fn: Callable[[Task], Any], agent: str | None = None, execution: Execution | None = None) -> Any:
        job = self.jobs.submit(task=task, agent=agent)
        if execution is not None:
            execution.jobs[job.job_id] = job
        if agent is not None and not self.agents.dispatch(agent, job.job_id):
            raise RuntimeError(f"agent {agent!r} is not available for dispatch")
        try:
            attempt = 0
            while True:
                attempt += 1
                job.attempts = attempt
                job.status = "running"
                try:
                    result = fn(task)
                    job.result = result
                    job.status = "completed"
                    task.status = "completed"
                    task.result = result
                    return result
                except Exception as exc:
                    job.error = str(exc)
                    task.status = "failed"
                    if self.retry.should_retry(attempt, exc):
                        delay = self.retry.next_delay(attempt)
                        job.metadata.setdefault("delays", []).append(delay)
                        continue
                    job.status = "failed"
                    raise
        finally:
            if agent is not None:
                self.agents.release(agent, job.job_id)

    # -- plan execution ------------------------------------------------------

    def execute_plan(
        self,
        plan: WorkflowPlan,
        tasks: list[Task],
        fn: Callable[[Task], Any] | None = None,
        mode: str = "sequential",
        agent: str | None = None,
        checkpoint_every: int = 2,
    ) -> Execution:
        if mode not in EXECUTION_MODES:
            raise ValueError(f"unknown execution mode {mode!r}; expected one of {EXECUTION_MODES}")
        fn = fn if fn is not None else (lambda t: t.params)
        execution = Execution(execution_id=f"exec-{len(self._executions) + 1}")
        self._executions[execution.execution_id] = execution
        execution.status = "running"

        by_id = {t.task_id: t for t in tasks}
        levels = self._levels(plan)
        completed: set[str] = set()
        try:
            for level in sorted(levels):
                level_ids = [tid for tid in levels[level] if tid not in completed]
                if not level_ids:
                    continue
                results = self._run_level(level_ids, by_id, fn, execution, mode, agent)
                for tid in level_ids:
                    if tid in results:
                        completed.add(tid)
                        execution.completed.append(tid)
                if checkpoint_every and len(completed) % checkpoint_every == 0:
                    self.checkpoints.save({"completed": sorted(completed)}, label=f"level {level}")
            execution.status = "completed"
        except Exception as exc:
            execution.status = "failed"
            execution.metadata["error"] = str(exc)
            undone = self.rollback.undo_all()
            execution.metadata["rolled_back"] = undone
        execution.updated_at = time.time()
        return execution

    def _run_level(
        self,
        task_ids: list[str],
        by_id: dict[str, Task],
        fn: Callable[[Task], Any],
        execution: Execution,
        mode: str,
        agent: str | None,
    ) -> dict[str, Any]:
        if mode == "parallel":
            fns = {tid: (lambda task=by_id[tid]: self._run_task(task, fn, agent=agent, execution=execution)) for tid in task_ids}
            return self.parallel.execute_many(fns)
        results: dict[str, Any] = {}
        for tid in task_ids:
            results[tid] = self._run_task(by_id[tid], fn, agent=agent, execution=execution)
        return results

    @staticmethod
    def _levels(plan: WorkflowPlan) -> dict[int, list[str]]:
        levels: dict[int, list[str]] = {}
        for step in plan.steps:
            levels.setdefault(step.level, []).append(step.task_id)
        return levels

    # -- introspection --------------------------------------------------------

    def get_execution(self, execution_id: str) -> Optional[Execution]:
        return self._executions.get(execution_id)

    def list_executions(self) -> list[Execution]:
        return [self._executions[eid] for eid in sorted(self._executions)]

    def snapshot(self) -> dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "retry": self.retry.to_dict(),
            "executions": {
                eid: {"status": e.status, "jobs": len(e.jobs), "completed": len(e.completed)}
                for eid, e in sorted(self._executions.items())
            },
            "jobs": self.jobs.stats(),
            "agents": self.agents.stats(),
            "nodes": self.distributed.stats(),
            "checkpoints": len(self.checkpoints.list()),
        }
