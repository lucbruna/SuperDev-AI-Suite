"""Tests for automation: tick cadence and task behaviour."""
from __future__ import annotations

from modules.self_healing_engine.automation import (
    AutomationRunner,
    CleanupTask,
    ContinuousValidationTask,
    OptimizationTask,
)
from modules.self_healing_engine.tests.helpers import make_context


class _RecordingTask:
    name = "recording"
    interval = 2
    last_run = 0
    runs = 0

    def run(self, ctx) -> None:
        self.runs += 1


def test_runner_tick_cadence() -> None:
    ctx = make_context()
    task = _RecordingTask()
    runner = AutomationRunner(tasks=[task])

    assert runner.tick(ctx) == 0  # tick 1: 1-0=1 < 2 -> nao roda
    assert task.runs == 0
    assert runner.tick(ctx) == 1  # tick 2: 2-0=2 >= 2 -> roda
    assert task.runs == 1
    assert runner.tick(ctx) == 0  # tick 3: 3-2=1 < 2 -> nao roda
    assert task.runs == 1


def test_cleanup_task_reports_without_deleting(tmp_path) -> None:
    ctx = make_context(tmp_path)
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()
    (cache_dir / "x.pyc").write_text("", encoding="utf-8")

    task = CleanupTask()
    task.run(ctx)
    assert cache_dir.exists()  # allow_destructive_operations = False (default)

    published = ctx.events.history_of("automation.cleanup")
    assert len(published) == 1
    payload = published[0].payload
    assert payload["candidate_count"] >= 1
    assert payload["removed"] is False


def test_continuous_validation_runs_on_project(tmp_path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "mod.py").write_text("x = 1\n", encoding="utf-8")
    (project / "__pycache__").mkdir()

    ctx = make_context(project)
    task = ContinuousValidationTask()
    task.run(ctx)

    assert ctx.events.history_of("automation.validation")


def test_optimization_task_publishes() -> None:
    ctx = make_context()
    OptimizationTask().run(ctx)
    assert ctx.events.history_of("automation.optimization")
