"""Tests for the deterministic scheduler (Phase H)."""
from __future__ import annotations

from modules.autonomous_developer.scheduler import Job, Scheduler


class TestScheduler:
    def test_register_names_unregister(self):
        scheduler = Scheduler()
        scheduler.register("a", interval_seconds=2)
        scheduler.register("b")
        assert scheduler.names() == ["a", "b"]
        assert scheduler.unregister("a") is True
        assert scheduler.unregister("a") is False
        assert scheduler.names() == ["b"]

    def test_register_overwrites(self):
        scheduler = Scheduler()
        scheduler.register("a", interval_seconds=2)
        job = scheduler.register("a", interval_seconds=5)
        assert scheduler.names() == ["a"]
        assert job.interval_seconds == 5

    def test_clock_starts_zero(self):
        assert Scheduler().clock() == 0.0

    def test_interval_job_schedule(self):
        scheduler = Scheduler()
        scheduler.register("a", interval_seconds=2)
        assert scheduler.tick(1) == []  # clock 1
        assert scheduler.tick(1) == ["a"]  # clock 2, due, next at 4
        assert scheduler.tick(1) == []  # clock 3
        assert scheduler.tick(1) == ["a"]  # clock 4
        assert scheduler.clock() == 4.0

    def test_one_shot_job_runs_every_tick(self):
        scheduler = Scheduler()
        scheduler.register("fast")
        assert scheduler.tick(1) == ["fast"]
        assert scheduler.tick(1) == ["fast"]

    def test_runs_counter(self):
        scheduler = Scheduler()
        scheduler.register("a", interval_seconds=1)
        scheduler.tick(1)
        scheduler.tick(1)
        scheduler.tick(1)
        assert scheduler._jobs["a"].runs == 3

    def test_next_run(self):
        scheduler = Scheduler()
        scheduler.register("a", interval_seconds=2)
        assert scheduler.next_run("a") == 2.0
        assert scheduler.next_run("missing") is None

    def test_unregistered_job_not_due(self):
        scheduler = Scheduler()
        scheduler.register("a", interval_seconds=1)
        scheduler.unregister("a")
        assert scheduler.tick(1) == []

    def test_tick_no_jobs(self):
        assert Scheduler().tick(1) == []

    def test_multiple_jobs_due_together(self):
        scheduler = Scheduler()
        scheduler.register("a", interval_seconds=1)
        scheduler.register("b", interval_seconds=2)
        assert scheduler.tick(1) == ["a"]
        assert scheduler.tick(1) == ["a", "b"]
        assert scheduler.tick(1) == ["a"]

    def test_job_dataclass_defaults(self):
        job = Job(name="x")
        assert job.interval_seconds == 0.0
        assert job.runs == 0
