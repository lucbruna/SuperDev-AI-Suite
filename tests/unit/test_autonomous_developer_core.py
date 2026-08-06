"""Tests for the Autonomous Developer core package (Phase B)."""
from __future__ import annotations

from modules.autonomous_developer.config.constants import (
    OP_MODIFY,
    PHASE_IMPLEMENT,
    PHASE_PLAN,
    PHASE_REVIEW,
    PHASE_TEST,
    TASK_BLOCKED,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_PENDING,
)
from modules.autonomous_developer.core import (
    DeveloperContext,
    DeveloperError,
    DeveloperMemory,
    DeveloperRegistry,
    DeveloperRuntime,
    DeveloperSession,
    DeveloperState,
    DeveloperStateTracker,
    EventBus,
    FileChange,
    PlanningError,
    ReviewVerdict,
    SessionManager,
    Task,
    TaskPlan,
    build_runtime,
    default_registry,
    register_decorator,
)
from modules.autonomous_developer.core.state import StateTransition


class TestExceptions:
    def test_developer_error_carries_context(self) -> None:
        err = DeveloperError("boom", context={"phase": "plan"})
        assert str(err) == "boom"
        assert err.context == {"phase": "plan"}

    def test_typed_subclass(self) -> None:
        err = PlanningError("cannot plan")
        assert isinstance(err, DeveloperError)


class TestEventBus:
    def test_subscribe_and_publish(self) -> None:
        bus = EventBus()
        seen = []
        bus.subscribe("task.started", lambda e: seen.append(e.type))
        bus.publish("task.started", {"goal": "x"})
        assert seen == ["task.started"]

    def test_wildcard_subscriber(self) -> None:
        bus = EventBus()
        seen = []
        bus.subscribe("*", lambda e: seen.append(e.type))
        bus.publish("a", {})
        bus.publish("b", {})
        assert seen == ["a", "b"]

    def test_unsubscribe(self) -> None:
        bus = EventBus()
        seen = []

        def handler(event) -> None:
            seen.append(event.type)

        bus.subscribe("e", handler)
        bus.unsubscribe("e", handler)
        bus.publish("e", {})
        assert seen == []

    def test_history_newest_first_and_filter(self) -> None:
        bus = EventBus()
        for i in range(3):
            bus.publish("phase.started", {"i": i})
        bus.publish("task.failed", {})
        hist = bus.history(limit=10)
        assert [e.type for e in hist] == ["task.failed", "phase.started", "phase.started", "phase.started"]
        only_failed = bus.history(event_type="task.failed")
        assert len(only_failed) == 1
        assert bus.history_size == 4

    def test_handling_bounded_history(self) -> None:
        bus = EventBus(history_size=2)
        for i in range(5):
            bus.publish("e", {"i": i})
        assert bus.history_size == 2

    def test_failing_handler_does_not_break_publish(self) -> None:
        bus = EventBus()

        def bad(event) -> None:
            raise RuntimeError("nope")

        seen = []
        bus.subscribe("e", bad)
        bus.subscribe("e", lambda e: seen.append(e.type))
        bus.publish("e", {})
        assert seen == ["e"]


class TestStateTracker:
    def test_initial_state(self) -> None:
        tracker = DeveloperStateTracker()
        assert tracker.state == DeveloperState.UNINITIALIZED
        assert tracker.elapsed_seconds == 0.0

    def test_transitions_recorded(self) -> None:
        tracker = DeveloperStateTracker()
        tracker.set_state(DeveloperState.PLANNING, context="plan")
        tracker.set_state(DeveloperState.IMPLEMENTING)
        transitions = tracker.transitions()
        assert len(transitions) == 2
        assert transitions[0].from_state == "uninitialized"
        assert transitions[0].to_state == "planning"
        assert transitions[0].context == "plan"
        assert isinstance(transitions[0], StateTransition)

    def test_terminal_state_sets_finished(self) -> None:
        tracker = DeveloperStateTracker()
        tracker.set_state(DeveloperState.PLANNING)
        tracker.set_state(DeveloperState.READY)
        assert tracker.state == DeveloperState.READY
        assert tracker.finished_at is not None
        assert tracker.elapsed_seconds >= 0.0
        assert DeveloperState.READY.terminal is True

    def test_error_records_context(self) -> None:
        tracker = DeveloperStateTracker()
        tracker.set_state(DeveloperState.PLANNING)
        tracker.mark_error("bad", context={"phase": "plan"})
        assert tracker.state == DeveloperState.ERROR
        assert tracker.last_error == "bad"
        assert tracker.last_error_context == {"phase": "plan"}
        assert DeveloperState.ERROR.terminal is True

    def test_clear_error_on_recovery(self) -> None:
        tracker = DeveloperStateTracker()
        tracker.mark_error("bad")
        tracker.set_state(DeveloperState.IDLE)
        assert tracker.last_error == ""

    def test_reset(self) -> None:
        tracker = DeveloperStateTracker()
        tracker.set_state(DeveloperState.PLANNING)
        tracker.mark_error("bad")
        tracker.reset()
        assert tracker.state == DeveloperState.IDLE
        assert tracker.transitions() == []
        assert tracker.last_error == ""

    def test_to_dict_shape(self) -> None:
        tracker = DeveloperStateTracker()
        tracker.set_state(DeveloperState.PLANNING)
        data = tracker.to_dict()
        assert data["state"] == "planning"
        assert data["transition_count"] == 1


class TestModels:
    def test_file_change(self) -> None:
        change = FileChange(path="src/a.py", content="print(1)", operation=OP_MODIFY)
        assert change.content_size == 8
        data = change.to_dict()
        assert data["path"] == "src/a.py"
        assert data["operation"] == "modify"
        assert "content" not in data

    def test_task_lifecycle(self) -> None:
        task = Task(title="t")
        assert task.status == TASK_PENDING
        assert task.is_done is False
        task.start()
        assert task.status == "in_progress"
        assert task.started_at is not None
        task.complete()
        assert task.status == TASK_COMPLETED
        assert task.is_done is True
        assert task.finished_at is not None

    def test_task_fail_and_block(self) -> None:
        task = Task()
        task.fail("oops")
        assert task.status == TASK_FAILED
        assert task.error == "oops"
        task2 = Task()
        task2.block("waiting")
        assert task2.status == TASK_BLOCKED

    def test_task_files_and_elapsed(self) -> None:
        task = Task()
        task.add_file(FileChange(path="x.py", content="def f(): pass"))
        assert len(task.files) == 1
        assert task.elapsed_seconds == 0.0
        task.start()
        assert task.elapsed_seconds >= 0.0

    def test_task_plan_summary(self) -> None:
        plan = TaskPlan(goal="add feature")
        plan.add_task(Task(title="a"))
        task = Task(title="b")
        task.complete()
        plan.add_task(task)
        summary = plan.summary()
        assert summary["task_count"] == 2
        assert summary["by_status"][TASK_COMPLETED] == 1
        assert len(plan.by_status(TASK_PENDING)) == 1
        assert plan.to_dict()["goal"] == "add feature"

    def test_review_verdict(self) -> None:
        verdict = ReviewVerdict(task_id="t1")
        assert verdict.approved is False
        approved = ReviewVerdict(task_id="t1", verdict="approved")
        assert approved.approved is True
        assert approved.to_dict()["reviewer"] == "autonomous_developer"


class TestRegistry:
    def test_register_and_get(self) -> None:
        registry = DeveloperRegistry()
        registry.register("planner", "default", object())
        assert registry.get("planner", "DEFAULT") is not None

    def test_duplicate_raises(self) -> None:
        registry = DeveloperRegistry()
        registry.register("planner", "default", object())
        try:
            registry.register("planner", "default", object())
            assert False, "expected DeveloperError"
        except DeveloperError as exc:
            assert "already registered" in str(exc)

    def test_replace_allowed(self) -> None:
        registry = DeveloperRegistry()
        registry.register("planner", "default", object(), replace=True)
        registry.register("planner", "default", object(), replace=True)

    def test_unknown_kind_raises(self) -> None:
        registry = DeveloperRegistry()
        try:
            registry.register("bogus", "x", object())
            assert False
        except DeveloperError:
            pass
        try:
            registry.get("bogus", "x")
            assert False
        except DeveloperError:
            pass

    def test_missing_component_raises(self) -> None:
        registry = DeveloperRegistry()
        try:
            registry.get("planner", "nope")
            assert False
        except DeveloperError as exc:
            assert "No planner" in str(exc)

    def test_all_names_counts_has(self) -> None:
        registry = DeveloperRegistry()
        registry.register("planner", "b", object())
        registry.register("planner", "a", object())
        registry.register("generator", "default", object())
        assert registry.names("planner") == ["a", "b"]
        counts = registry.counts()
        assert counts["planner"] == 2
        assert counts["generator"] == 1
        assert counts["reviewer"] == 0
        assert registry.has("planner", "a") is True
        assert registry.has("planner", "z") is False

    def test_reset(self) -> None:
        registry = DeveloperRegistry()
        registry.register("planner", "a", object())
        registry.reset()
        assert registry.counts() == {kind: 0 for kind in (
            "planner", "generator", "validator", "reviewer",
            "executor", "agent", "documenter", "tool",
        )}

    def test_default_registry_singleton(self) -> None:
        assert default_registry() is default_registry()

    def test_register_decorator(self) -> None:
        @register_decorator("tool", "my_tool")
        def my_tool(ctx, **kwargs):
            return "ok"

        assert default_registry().get("tool", "my_tool") is my_tool


class TestMemory:
    def test_put_get_contains(self) -> None:
        memory = DeveloperMemory()
        memory.put("k", {"v": 1})
        assert memory.get("k") == {"v": 1}
        assert memory.contains("k") is True
        assert memory.get("missing", "d") == "d"

    def test_lru_eviction(self) -> None:
        memory = DeveloperMemory(capacity=2)
        memory.put("a", 1)
        memory.put("b", 2)
        memory.get("a")
        memory.put("c", 3)
        assert memory.contains("b") is False
        assert memory.contains("a") is True

    def test_evict_and_clear(self) -> None:
        memory = DeveloperMemory()
        memory.put("a", 1)
        assert memory.evict("a") is True
        assert memory.evict("a") is False
        memory.put("b", 2)
        memory.clear()
        assert memory.is_empty

    def test_setdefault(self) -> None:
        memory = DeveloperMemory()
        assert memory.setdefault("a", "x") == "x"
        assert memory.setdefault("a", "y") == "x"

    def test_stats(self) -> None:
        memory = DeveloperMemory(capacity=10)
        memory.put("a", "hello", size_bytes=5)
        stats = memory.stats()
        assert stats["entries"] == 1
        assert stats["capacity"] == 10
        assert stats["bytes"] == 5
        assert stats["usage_ratio"] == 0.1


class TestSessions:
    def test_create_complete(self) -> None:
        manager = SessionManager()
        session = manager.create(project_root="/repo", goal="add x")
        assert session.status == "running"
        assert session.goal == "add x"
        manager.complete(session, success=True)
        assert session.status == "completed"
        assert session.finished_at is not None
        assert manager.get(session.session_id) is None

    def test_active_and_recent(self) -> None:
        manager = SessionManager()
        s1 = manager.create(goal="a")
        s2 = manager.create(goal="b")
        manager.complete(s2, success=False)
        assert len(manager.active()) == 1
        recent = manager.recent(limit=5)
        assert len(recent) == 2
        assert recent[0].session_id == s2.session_id  # newest first

    def test_cancel(self) -> None:
        manager = SessionManager()
        session = manager.create(goal="x")
        manager.cancel(session)
        assert session.status == "cancelled"
        assert manager.active() == []

    def test_close_all(self) -> None:
        manager = SessionManager()
        manager.create(goal="a")
        manager.create(goal="b")
        manager.close_all()
        assert manager.active() == []
        assert all(s.status == "failed" for s in manager.recent())

    def test_session_to_dict(self) -> None:
        session = DeveloperSession(goal="g", status="running")
        data = session.to_dict()
        assert data["goal"] == "g"
        assert "elapsed_seconds" in data
        assert session.elapsed_seconds >= 0.0


class TestContext:
    def test_defaults(self) -> None:
        runtime = DeveloperRuntime()
        ctx = runtime.context
        assert isinstance(ctx, DeveloperContext)
        assert ctx.bus.history_size == 0
        assert ctx.artifacts == {}

    def test_create_session_uses_project_root(self, tmp_path) -> None:
        runtime = DeveloperRuntime()
        runtime.config.resolve(str(tmp_path))
        runtime.context = DeveloperContext(config=runtime.config)
        session = runtime.context.create_session(goal="g")
        assert session.project_root == str(tmp_path.resolve())

    def test_record_and_artifacts(self) -> None:
        runtime = DeveloperRuntime()
        ctx = runtime.context
        ctx.record("files", 3)
        assert ctx.stats["files"] == 3
        ctx.set_artifact("plan", {"ok": True})
        assert ctx.get_artifact("plan") == {"ok": True}
        assert ctx.get_artifact("nope", 1) == 1

    def test_cancel(self) -> None:
        runtime = DeveloperRuntime()
        ctx = runtime.context
        seen = []
        ctx.bus.subscribe("task.cancelled", lambda e: seen.append(e.type))
        ctx.request_cancel()
        assert ctx.cancelled is True
        assert seen == ["task.cancelled"]


# ── Stub phase components ────────────────────────────────────────────────────

class StubPlanner:
    def run(self, ctx, **kwargs):
        plan = TaskPlan(goal=kwargs.get("goal", ""))
        plan.add_task(Task(title="generated task"))
        return plan


class StubGenerator:
    def run(self, ctx, **kwargs):
        return {"written": ["src/app.py"]}


class StubValidator:
    def run(self, ctx, **kwargs):
        return {"passed": 3, "failed": 0}


class StubReviewer:
    def run(self, ctx, **kwargs):
        return ReviewVerdict(task_id="t1", verdict="approved")


class FailingComponent:
    def run(self, ctx, **kwargs):
        raise PlanningError("cannot decompose")


class TestRuntime:
    def _configured_runtime(self, tmp_path) -> DeveloperRuntime:
        runtime = DeveloperRuntime()
        runtime.config.resolve(str(tmp_path))
        # Fresh registry per runtime so the shared default registry singleton
        # cannot leak components between tests.
        runtime.context = DeveloperContext(
            config=runtime.config, registry=DeveloperRegistry()
        )
        return runtime

    def _register_default_components(self, runtime: DeveloperRuntime) -> None:
        runtime.registry.register("planner", "default", StubPlanner(), replace=True)
        runtime.registry.register("generator", "default", StubGenerator(), replace=True)
        runtime.registry.register("validator", "default", StubValidator(), replace=True)
        runtime.registry.register("reviewer", "default", StubReviewer(), replace=True)

    def test_execute_runs_all_phases(self, tmp_path) -> None:
        runtime = self._configured_runtime(tmp_path)
        self._register_default_components(runtime)
        ctx = runtime.execute("implement feature x")
        assert ctx.state.state == DeveloperState.READY
        assert ctx.artifacts[PHASE_PLAN].goal == "implement feature x"
        assert ctx.artifacts[PHASE_IMPLEMENT]["written"] == ["src/app.py"]
        assert ctx.artifacts[PHASE_TEST]["passed"] == 3
        assert ctx.artifacts[PHASE_REVIEW].approved is True
        # Session lifecycle
        sessions = runtime.sessions.recent(limit=1)
        assert sessions and sessions[0].status == "completed"

    def test_execute_emits_events_in_order(self, tmp_path) -> None:
        runtime = self._configured_runtime(tmp_path)
        self._register_default_components(runtime)
        runtime.execute("go")
        types = [e.type for e in runtime.bus.history(limit=20)]
        # history() returns newest first.
        expected = ["task.completed"] + ["phase.completed", "phase.started"] * 4 + ["task.started"]
        assert types == expected

    def test_missing_component_fails_gracefully(self, tmp_path) -> None:
        runtime = self._configured_runtime(tmp_path)
        # Only a planner registered; implement is missing.
        runtime.registry.register("planner", "default", StubPlanner(), replace=True)
        runtime.execute("go")
        assert runtime.state.state == DeveloperState.ERROR
        assert runtime.state.last_error
        sessions = runtime.sessions.recent(limit=1)
        assert sessions and sessions[0].status == "failed"
        failed = [e for e in runtime.bus.history() if e.type == "task.failed"]
        assert len(failed) == 1

    def test_failing_component_marks_error(self, tmp_path) -> None:
        runtime = self._configured_runtime(tmp_path)
        runtime.registry.register("planner", "default", FailingComponent(), replace=True)
        runtime.execute("go")
        assert runtime.state.state == DeveloperState.ERROR
        assert "cannot decompose" in runtime.state.last_error
        assert PHASE_IMPLEMENT not in runtime.context.artifacts

    def test_cancel_stops_flow(self, tmp_path) -> None:
        runtime = self._configured_runtime(tmp_path)

        class CancellingPlanner:
            def run(self, ctx, **kwargs):
                ctx.request_cancel()
                return TaskPlan(goal="x")

        runtime.registry.register("planner", "default", CancellingPlanner(), replace=True)
        runtime.registry.register("generator", "default", StubGenerator(), replace=True)
        ctx = runtime.execute("go")
        assert PHASE_IMPLEMENT not in ctx.artifacts
        assert ctx.state.state == DeveloperState.READY
        assert "task.cancelled" in [e.type for e in runtime.bus.history()]
        sessions = runtime.sessions.recent(limit=1)
        assert sessions and sessions[0].status == "cancelled"

    def test_unknown_phase_raises(self, tmp_path) -> None:
        runtime = self._configured_runtime(tmp_path)
        try:
            runtime.run_phase("bogus")
            assert False
        except DeveloperError as exc:
            assert "Unknown phase" in str(exc)

    def test_custom_phase_list(self, tmp_path) -> None:
        runtime = self._configured_runtime(tmp_path)
        self._register_default_components(runtime)
        runtime.execute("go", phases=(PHASE_PLAN, PHASE_REVIEW))
        assert PHASE_IMPLEMENT not in runtime.context.artifacts
        assert PHASE_REVIEW in runtime.context.artifacts

    def test_status_shape(self, tmp_path) -> None:
        runtime = self._configured_runtime(tmp_path)
        status = runtime.status()
        assert status["state"]["state"] == "uninitialized"
        assert status["config"]["mode"] == "supervised"
        assert status["config"]["allow_main_branch_writes"] is False
        assert "registry" in status

    def test_reset(self, tmp_path) -> None:
        runtime = self._configured_runtime(tmp_path)
        self._register_default_components(runtime)
        runtime.execute("go")
        runtime.reset()
        assert runtime.state.state == DeveloperState.IDLE
        assert runtime.context.artifacts == {}
        assert runtime.sessions.active() == []

    def test_build_runtime_factory(self) -> None:
        runtime = build_runtime()
        assert isinstance(runtime, DeveloperRuntime)
        assert runtime.config.project_root
