"""Tests for the executor/ subpackage (Volume 31, Fase 3)."""

from __future__ import annotations

from agent_orchestration.executor import ActionManager, CommandRunner, ExecutorEngine, TaskExecutor, WorkflowRunner
from agent_orchestration.orchestrator_events import OrchestratorEvents, OrchestratorEventType
from agent_orchestration.orchestrator_models import AgentTask, TaskStatus


def _task(task_id: str, agent_id: str = "agent-1",
          dependencies: list[str] | None = None) -> AgentTask:
    return AgentTask(task_id=task_id, title=f"Tarefa {task_id}",
                     agent_id=agent_id,
                     dependencies=list(dependencies or []))


class TestTaskExecutor:
    def test_default_runner_completes(self):
        result = TaskExecutor().execute(_task("t1"))
        assert result.status == TaskStatus.COMPLETED
        assert result.task_id == "t1"
        assert result.error == ""

    def test_runner_failure_marks_failed(self):
        def failing(_task):
            raise ValueError("boom")

        result = TaskExecutor(failing).execute(_task("t2"))
        assert result.status == TaskStatus.FAILED
        assert "boom" in result.error

    def test_attempts_incremented(self):
        task = _task("t3")
        TaskExecutor().execute(task)
        assert task.attempts == 1

    def test_task_state_updated(self):
        task = _task("t4")
        TaskExecutor().execute(task)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == "ok:Tarefa t4"


class TestCommandRunner:
    def test_dry_run(self):
        result = CommandRunner(dry_run=True).run("echo oi")
        assert result["ok"] is True
        assert result["dry_run"] is True

    def test_successful_command(self):
        result = CommandRunner().run('python -c "print(1)"')
        assert result["ok"] is True
        assert result["output"] == "1"

    def test_failing_command(self):
        result = CommandRunner().run('python -c "import sys; sys.exit(3)"')
        assert result["ok"] is False
        assert result["returncode"] == 3

    def test_shell_metacharacters_not_executed_by_default(self):
        # CWE-78 regression: '&&' must be passed as an argument, not executed.
        result = CommandRunner().run('python -c "print(1)" && echo pwned')
        assert result["ok"] is True
        assert result["output"] == "1"
        assert "pwned" not in result["output"]

    def test_shell_true_still_supported(self):
        result = CommandRunner().run("echo oi", shell=True)
        assert result["ok"] is True
        assert result["output"] == "oi"


class TestActionManager:
    def test_register_and_execute(self):
        manager = ActionManager()
        manager.register("soma", lambda a, b: a + b)
        result = manager.execute("soma", a=2, b=3)
        assert result == {"ok": True, "action": "soma", "data": 5}

    def test_unknown_action(self):
        result = ActionManager().execute("nope")
        assert result["ok"] is False
        assert result["error"] == "unknown_action"

    def test_action_error_isolation(self):
        manager = ActionManager()
        manager.register("falha", lambda: 1 / 0)
        result = manager.execute("falha")
        assert result["ok"] is False
        assert "division" in result["error"] or "zero" in result["error"]

    def test_unregister(self):
        manager = ActionManager()
        manager.register("x", lambda: 1)
        assert manager.unregister("x") is True
        assert manager.unregister("x") is False


class TestWorkflowRunner:
    def test_respects_dependencies(self):
        tasks = [_task("a", dependencies=["b"]), _task("b")]
        results = WorkflowRunner().run(tasks)
        order = [result.task_id for result in results]
        assert order == ["b", "a"]
        assert all(result.status == TaskStatus.COMPLETED
                   for result in results)

    def test_cycle_keeps_remaining_tasks(self):
        tasks = [_task("x", dependencies=["y"]),
                 _task("y", dependencies=["x"])]
        results = WorkflowRunner().run(tasks)
        assert len(results) == 2

    def test_summary_counts(self):
        results = WorkflowRunner().run([_task("s1"), _task("s2")])
        summary = WorkflowRunner().summary(results)
        assert summary["total"] == 2
        assert summary["completed"] == 2
        assert summary["failed"] == 0

    def test_run_then_callback(self):
        done: list[str] = []
        WorkflowRunner().run_then(
            [_task("c1")], lambda result: done.append(result.task_id))
        assert done == ["c1"]


class TestExecutorEngine:
    def test_execute_emits_events(self):
        events = OrchestratorEvents()
        seen: list[str] = []
        events.on(OrchestratorEventType.TASK_STARTED,
                  lambda _payload: seen.append("started"))
        events.on(OrchestratorEventType.TASK_COMPLETED,
                  lambda _payload: seen.append("completed"))
        engine = ExecutorEngine(events=events)
        result = engine.execute(_task("e1"))
        assert result.status == TaskStatus.COMPLETED
        assert seen == ["started", "completed"]

    def test_failure_emits_failed_event(self):
        events = OrchestratorEvents()
        seen: list[str] = []
        events.on(OrchestratorEventType.TASK_FAILED,
                  lambda _payload: seen.append("failed"))
        engine = ExecutorEngine(events=events, executor=TaskExecutor(
            lambda _task: (_ for _ in ()).throw(RuntimeError("nope"))))
        result = engine.execute(_task("e2"))
        assert result.status == TaskStatus.FAILED
        assert seen == ["failed"]

    def test_metrics_counters(self):
        engine = ExecutorEngine()
        engine.execute(_task("e3"))
        engine.run_command("echo ok")
        engine.register_action("dobro", lambda x: x * 2)
        engine.execute_action("dobro", x=4)
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("ao.tasks_started") == 1
        assert counters.get("ao.tasks_completed") == 1
        assert counters.get("ao.commands") == 1
        assert counters.get("ao.actions") == 1

    def test_run_workflow_summary(self):
        engine = ExecutorEngine()
        summary = engine.run_workflow([_task("w1"), _task("w2")])
        assert summary["total"] == 2
        assert summary["completed"] == 2

    def test_stats(self):
        engine = ExecutorEngine()
        engine.register_action("a", lambda: 1)
        stats = engine.stats()
        assert stats["actions"]["actions"] == 1
        assert "metrics" in stats
