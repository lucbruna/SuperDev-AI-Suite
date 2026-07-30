from __future__ import annotations

from workflow.workers.worker_task import WorkerTask
from workflow.workers.worker_state import WorkerState
from workflow.workers.worker_health import WorkerHealth
from workflow.workers.worker_metrics import WorkerMetrics


class TestWorkers:
    def test_worker_task_execute(self) -> None:
        calls: list[str] = []
        task = WorkerTask(action=lambda: calls.append("done"))
        task.execute()
        assert task.succeeded
        assert task.result is None
        assert len(calls) == 1

    def test_worker_task_failure(self) -> None:
        def fail() -> None:
            raise ValueError("fail")
        task = WorkerTask(action=fail)
        task.execute()
        assert not task.succeeded
        assert task.error == "fail"

    def test_worker_state_enum(self) -> None:
        assert WorkerState.IDLE.value == "idle"
        assert WorkerState.BUSY.value == "busy"
        assert WorkerState.ERROR.value == "error"

    def test_worker_health(self) -> None:
        h = WorkerHealth()
        h.report("w1", WorkerState.IDLE)
        assert h.is_healthy("w1")
        h.report("w1", WorkerState.ERROR)
        assert not h.is_healthy("w1")

    def test_worker_metrics(self) -> None:
        m = WorkerMetrics()
        m.record_submission()
        m.record_completion()
        snap = m.snapshot()
        assert snap["submissions"] == 1
        assert snap["completions"] == 1
