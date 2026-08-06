"""Long-term lessons: recorded on failure, consumed by the planner."""
from __future__ import annotations

from pathlib import Path

from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.exceptions import DeveloperError
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.core.runtime import DeveloperRuntime
from modules.autonomous_developer.generator.generator import GenerationResult
from modules.autonomous_developer.memory.lessons import (
    Lesson,
    LessonStore,
    format_lessons,
)
from modules.autonomous_developer.planner.project_planner import ProjectPlanner


class StubGenerator:
    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        return GenerationResult(written=[])


class FailingValidator:
    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        ctx.record("tests_failed", 2)
        raise DeveloperError("Repo tests failed: 2 failed, 0 passed")


class TestLessonStore:
    def test_add_and_dedupe(self):
        store = LessonStore()
        first = Lesson(phase="test", goal="Fix the sum function", error="e1")
        duplicate = Lesson(phase="test", goal="fix the SUM function", error="e2")
        other = Lesson(phase="review", goal="Fix the sum function", error="e3")
        assert store.add(first) is True
        assert store.add(duplicate) is False  # same phase + goal
        assert store.add(other) is True  # different phase
        assert len(store.all()) == 2

    def test_for_goal_token_match(self):
        store = LessonStore()
        store.add(Lesson(phase="test", goal="Fix add() in the calculator", error="e"))
        assert len(store.for_goal("Fix the calculator add function")) == 1
        assert store.for_goal("completely unrelated task") == []

    def test_bounded(self):
        store = LessonStore(max_lessons=3)
        for i in range(5):
            store.add(Lesson(phase="test", goal=f"Goal number {i}", error=f"e{i}"))
        assert len(store.all()) == 3

    def test_format_lessons(self):
        store = LessonStore()
        store.add(Lesson(phase="test", goal="Fix x", error="tests failed", lesson="run the tests"))
        block = format_lessons(store.for_goal("Fix x"))
        assert "Previous failures to avoid" in block
        assert "run the tests" in block
        assert format_lessons([]) == ""


def _failing_runtime(tmp_path: Path) -> DeveloperRuntime:
    registry = DeveloperRegistry()
    registry.register("planner", "default", ProjectPlanner())
    registry.register("generator", "default", StubGenerator())
    registry.register("validator", "default", FailingValidator())
    config = DeveloperConfig(
        project_root=str(tmp_path),
        run_tests=True,
        run_review=True,
        create_pr=False,
    )
    return DeveloperRuntime(config=config, registry=registry)


class TestLoopWiring:
    def test_failure_records_lesson_and_planner_consumes_it(self, tmp_path: Path):
        runtime = _failing_runtime(tmp_path)
        goal = "Fix add() so it returns the sum"

        ctx = runtime.execute(goal)
        # Session failed; lesson recorded from the task.failed event.
        assert ctx.state.to_dict()["state"] == "error"
        lessons = ctx.lessons.all()
        assert len(lessons) == 1
        assert lessons[0].phase == "test"
        assert lessons[0].goal == goal
        assert "failed" in lessons[0].error
        # First run had no prior lessons to consume.
        assert ctx.stats.get("lessons_used", 0) == 0

        # Second run over the same goal: the planner now sees the lesson.
        ctx2 = runtime.execute(goal)
        assert ctx2.lessons.stats()["lessons"] == 1  # deduped, not duplicated
        assert ctx2.stats.get("lessons_used", 0) == 1

        # Lessons surface in runtime status.
        status = runtime.status()
        assert status["lessons"]["lessons"] == 1

    def test_reset_clears_lessons(self, tmp_path: Path):
        runtime = _failing_runtime(tmp_path)
        runtime.execute("Fix add() so it returns the sum")
        assert runtime.context.lessons.stats()["lessons"] == 1
        runtime.reset()
        assert runtime.context.lessons.stats()["lessons"] == 0

    def test_success_records_no_lesson(self, tmp_path: Path):
        from modules.autonomous_developer.config.constants import (
            PHASE_IMPLEMENT,
            PHASE_PLAN,
            PHASE_TEST,
        )

        registry = DeveloperRegistry()
        registry.register("planner", "default", ProjectPlanner())
        registry.register("generator", "default", StubGenerator())

        class PassingValidator:
            def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
                ctx.record("tests_passed", 3)
                return {"passed": 3, "failed": 0}

        registry.register("validator", "default", PassingValidator())
        config = DeveloperConfig(
            project_root=str(tmp_path),
            run_tests=True,
            create_pr=False,
            allow_main_branch_writes=False,
        )
        runtime = DeveloperRuntime(config=config, registry=registry)
        runtime.execute(
            "Do something harmless",
            phases=(PHASE_PLAN, PHASE_IMPLEMENT, PHASE_TEST),
        )
        assert runtime.context.lessons.stats()["lessons"] == 0
