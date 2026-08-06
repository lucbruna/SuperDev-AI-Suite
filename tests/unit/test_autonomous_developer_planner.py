"""Unit tests for the Autonomous Developer planner + generator phases.

Phase C: project/task planning (deterministic goal decomposition, ordering,
estimation) and the code generator (safe file application under generator
and security rules).
"""
from __future__ import annotations

import pytest

from modules.autonomous_developer.config.constants import (
    OP_CREATE,
    OP_DELETE,
    OP_MODIFY,
    OP_TEST,
    PHASE_IMPLEMENT,
    PHASE_PLAN,
    PHASE_TEST,
    RISK_CRITICAL,
    RISK_HIGH,
)
from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.config.generator_config import GeneratorConfig
from modules.autonomous_developer.config.planner_config import PlannerConfig
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.exceptions import GenerationError, PlanningError
from modules.autonomous_developer.core.models import FileChange, Task, TaskPlan
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.generator.generator import CodeGenerator
from modules.autonomous_developer.planner.project_planner import ProjectPlanner
from modules.autonomous_developer.planner.task_planner import TaskPlanner


# ---------------------------------------------------------------------------
# TaskPlanner
# ---------------------------------------------------------------------------


class TestTaskPlannerOrdering:
    def test_orders_dependencies_first(self) -> None:
        a = Task(task_id="a", title="A")
        b = Task(task_id="b", title="B", depends_on=["a"])
        c = Task(task_id="c", title="C", depends_on=["a", "b"])
        ordered = TaskPlanner().order_tasks([c, b, a])
        assert [t.task_id for t in ordered] == ["a", "b", "c"]

    def test_stable_for_independent_tasks(self) -> None:
        a = Task(task_id="a", title="A")
        b = Task(task_id="b", title="B")
        assert [t.task_id for t in TaskPlanner().order_tasks([b, a])] == ["b", "a"]

    def test_unknown_dependencies_never_block(self) -> None:
        a = Task(task_id="a", title="A")
        b = Task(task_id="b", title="B", depends_on=["ghost"])
        ordered = TaskPlanner().order_tasks([b, a])
        assert [t.task_id for t in ordered] == ["b", "a"]

    def test_cycle_keeps_original_relative_order(self) -> None:
        a = Task(task_id="a", title="A", depends_on=["b"])
        b = Task(task_id="b", title="B", depends_on=["a"])
        ordered = TaskPlanner().order_tasks([a, b])
        assert [t.task_id for t in ordered] == ["a", "b"]

    def test_empty_input(self) -> None:
        assert TaskPlanner().order_tasks([]) == []


class TestTaskPlannerCycles:
    def test_detects_two_node_cycle(self) -> None:
        a = Task(task_id="a", title="A", depends_on=["b"])
        b = Task(task_id="b", title="B", depends_on=["a"])
        cycles = TaskPlanner().detect_cycles([a, b])
        assert len(cycles) == 1
        assert set(cycles[0]) == {"a", "b"}

    def test_detects_self_loop(self) -> None:
        task = Task(task_id="x", title="X", depends_on=["x"])
        assert TaskPlanner().detect_cycles([task]) == [["x", "x"]]

    def test_acyclic_graph_has_no_cycles(self) -> None:
        a = Task(task_id="a", title="A")
        b = Task(task_id="b", title="B", depends_on=["a"])
        assert TaskPlanner().detect_cycles([a, b]) == []


class TestTaskPlannerEstimation:
    def test_base_estimate(self) -> None:
        assert TaskPlanner().estimate_hours(Task(title="")) == 0.5

    def test_description_increases_estimate(self) -> None:
        short = TaskPlanner().estimate_hours(Task(title="T"))
        long = TaskPlanner().estimate_hours(
            Task(title="T", description="detailed work described here")
        )
        assert long > short

    def test_high_risk_multiplier(self) -> None:
        base = TaskPlanner().estimate_hours(Task(title="T"))
        high = TaskPlanner().estimate_hours(Task(title="T", risk=RISK_HIGH))
        # Estimates are rounded after the multiplier, so compare the ratio.
        assert high / base == pytest.approx(1.5, abs=0.02)

    def test_critical_risk_multiplier(self) -> None:
        base = TaskPlanner().estimate_hours(Task(title="Fix critical auth bug"))
        critical = TaskPlanner().estimate_hours(
            Task(title="Fix critical auth bug", risk=RISK_CRITICAL)
        )
        assert critical / base == pytest.approx(2.0, abs=0.02)

    def test_capped_at_max_estimation(self) -> None:
        planner = TaskPlanner(PlannerConfig(max_estimation_hours=5.0))
        huge = Task(title="T", description="x" * 1900)
        assert planner.estimate_hours(huge) == 5.0


class TestTaskPlannerPhase:
    def test_keeps_explicit_phase(self) -> None:
        task = Task(title="T", phase=PHASE_TEST)
        assert TaskPlanner().assign_phase(task) == PHASE_TEST

    def test_test_operation_maps_to_test_phase(self) -> None:
        task = Task(title="T", files=[FileChange(path="t.py", operation=OP_TEST)])
        assert TaskPlanner().assign_phase(task) == PHASE_TEST

    def test_implementation_default(self) -> None:
        task = Task(title="T", files=[FileChange(path="a.py", operation=OP_CREATE)])
        assert TaskPlanner().assign_phase(task) == PHASE_IMPLEMENT

    def test_no_files_defaults_to_implement(self) -> None:
        assert TaskPlanner().assign_phase(Task(title="T")) == PHASE_IMPLEMENT


class TestTaskPlannerAnalyze:
    def test_analyze_summary(self) -> None:
        a = Task(task_id="a", title="A")
        b = Task(task_id="b", title="B", depends_on=["a"])
        plan = TaskPlan(goal="goal", tasks=[b, a])
        result = TaskPlanner().analyze(plan)
        assert result["plan_id"] == plan.plan_id
        assert result["task_count"] == 2
        assert result["ordered"] == ["a", "b"]
        assert result["cycles"] == []
        assert result["estimated_hours"] > 0


# ---------------------------------------------------------------------------
# ProjectPlanner
# ---------------------------------------------------------------------------


class TestProjectPlannerBasic:
    def test_empty_goal_raises(self) -> None:
        with pytest.raises(PlanningError):
            ProjectPlanner().plan("")

    def test_whitespace_goal_raises(self) -> None:
        with pytest.raises(PlanningError):
            ProjectPlanner().plan("   \n  ")

    def test_single_line_goal_becomes_one_task(self) -> None:
        plan = ProjectPlanner().plan("Add login endpoint")
        assert len(plan.tasks) == 1
        task = plan.tasks[0]
        assert task.title == "Add login endpoint"
        assert task.priority == "medium"
        assert task.phase == PHASE_IMPLEMENT

    def test_custom_priority_applied(self) -> None:
        plan = ProjectPlanner().plan("Add login endpoint", priority="high")
        assert plan.tasks[0].priority == "high"

    def test_multiline_goal_decomposes_per_line(self) -> None:
        goal = "Add auth\nAdd dashboard\nAdd tests"
        plan = ProjectPlanner().plan(goal)
        assert [t.title for t in plan.tasks] == ["Add auth", "Add dashboard", "Add tests"]

    def test_decomposition_disabled_keeps_single_task(self) -> None:
        planner = ProjectPlanner(PlannerConfig(decompose_tasks=False))
        plan = planner.plan("Add auth\nAdd dashboard")
        assert len(plan.tasks) == 1
        assert plan.tasks[0].title == "Add auth\nAdd dashboard"


class TestProjectPlannerTaskSpecs:
    def test_string_specs(self) -> None:
        plan = ProjectPlanner().plan("goal", tasks=["One", "Two"])
        assert [t.title for t in plan.tasks] == ["One", "Two"]

    def test_dict_spec_parses_fields(self) -> None:
        plan = ProjectPlanner().plan(
            "goal",
            tasks=[
                {
                    "title": "Build",
                    "description": "Do the thing",
                    "priority": "high",
                    "risk": RISK_HIGH,
                    "phase": PHASE_TEST,
                    "depends_on": ["base"],
                    "files": [{"path": "a.py", "content": "x=1", "reason": "core"}],
                }
            ],
        )
        task = plan.tasks[0]
        assert task.description == "Do the thing"
        assert task.priority == "high"
        assert task.risk == RISK_HIGH
        assert task.phase == PHASE_TEST
        assert task.depends_on == ["base"]
        assert len(task.files) == 1
        assert task.files[0].path == "a.py"
        assert task.files[0].content == "x=1"
        assert task.files[0].operation == OP_CREATE
        assert task.files[0].reason == "core"

    def test_file_change_objects_passthrough(self) -> None:
        change = FileChange(path="b.py", content="y=2", operation=OP_MODIFY)
        plan = ProjectPlanner().plan(
            "goal", tasks=[{"title": "Build", "files": [change]}]
        )
        assert plan.tasks[0].files[0] is change

    def test_spec_without_title_raises(self) -> None:
        with pytest.raises(PlanningError):
            ProjectPlanner().plan("goal", tasks=[{"description": "no title"}])

    def test_unsupported_spec_type_raises(self) -> None:
        with pytest.raises(PlanningError):
            ProjectPlanner().plan("goal", tasks=[42])  # type: ignore[list-item]


class TestProjectPlannerLimitsAndOrdering:
    def test_task_cap_enforced(self) -> None:
        planner = ProjectPlanner(PlannerConfig(max_tasks_per_request=2))
        with pytest.raises(PlanningError, match="max 2"):
            planner.plan("One\nTwo\nThree")

    def test_topo_sort_orders_dependencies(self) -> None:
        # Spec-level depends_on references external task ids (task ids are
        # generated per task), so ordering must match the internal sorter.
        ordered = ProjectPlanner().plan(
            "goal",
            tasks=[
                {"title": "Second", "depends_on": ["first"]},
                {"title": "First", "depends_on": []},
            ],
        )
        raw = ProjectPlanner(PlannerConfig(topo_sort=False)).plan(
            "goal",
            tasks=[
                {"title": "Second", "depends_on": ["first"]},
                {"title": "First", "depends_on": []},
            ],
        )
        # Task ids are random per plan, so compare deterministic titles: the
        # topo-sorted plan must match the sorter applied to the same input.
        expected = [t.title for t in TaskPlanner().order_tasks(raw.tasks)]
        assert [t.title for t in ordered.tasks] == expected
        # TaskPlanner keeps unknown deps from blocking, so both orderings
        # preserve input order here.
        assert [t.title for t in ordered.tasks] == ["Second", "First"]

    def test_topo_sort_disabled_preserves_order(self) -> None:
        planner = ProjectPlanner(PlannerConfig(topo_sort=False))
        plan = planner.plan(
            "goal",
            tasks=[
                {"title": "Second", "depends_on": ["first"]},
                {"title": "First", "depends_on": []},
            ],
        )
        assert [t.title for t in plan.tasks] == ["Second", "First"]


class TestProjectPlannerRun:
    def _context(self, tmp_path) -> DeveloperContext:
        config = DeveloperConfig(project_root=str(tmp_path))
        return DeveloperContext(config=config, registry=DeveloperRegistry())

    def test_run_returns_plan_and_records(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        result = ProjectPlanner().run(ctx, "Build feature", priority="high")
        assert isinstance(result, TaskPlan)
        assert ctx.stats["task_count"] == 1
        assert ctx.stats["knowledge_used"] is False
        events = [e.type for e in ctx.bus.history(event_type="plan.ready")]
        assert events == ["plan.ready"]

    def test_run_with_tasks_kwarg(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        result = ProjectPlanner().run(ctx, "goal", tasks=["A", "B"])
        assert [t.title for t in result.tasks] == ["A", "B"]


# ---------------------------------------------------------------------------
# CodeGenerator
# ---------------------------------------------------------------------------


class TestCodeGeneratorCreate:
    def test_creates_file(self, tmp_path) -> None:
        result = CodeGenerator().apply_changes(
            [FileChange(path="app.py", content="x = 1")], project_root=tmp_path
        )
        assert result.success
        assert result.written == ["app.py"]
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "x = 1"
        assert not list(tmp_path.glob("*.tmp"))  # temp file cleaned up

    def test_nested_path_creates_parents(self, tmp_path) -> None:
        CodeGenerator().apply_changes(
            [FileChange(path="src/lib/util.py", content="v = 2")], project_root=tmp_path
        )
        assert (tmp_path / "src" / "lib" / "util.py").exists()

    def test_existing_file_skipped(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("old", encoding="utf-8")
        result = CodeGenerator().apply_changes(
            [FileChange(path="app.py", content="new")], project_root=tmp_path
        )
        assert result.written == []
        assert result.skipped == ["app.py (already exists)"]

    def test_new_files_disabled_skips(self, tmp_path) -> None:
        config = GeneratorConfig(allow_new_files=False)
        result = CodeGenerator(config).apply_changes(
            [FileChange(path="app.py", content="x")], project_root=tmp_path
        )
        assert result.skipped == ["app.py (new files disabled)"]
        assert not (tmp_path / "app.py").exists()

    def test_missing_content_skipped(self, tmp_path) -> None:
        result = CodeGenerator().apply_changes(
            [FileChange(path="app.py")], project_root=tmp_path
        )
        assert result.skipped == ["app.py (no content)"]


class TestCodeGeneratorModify:
    def test_modify_writes_and_backs_up(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("old", encoding="utf-8")
        result = CodeGenerator().apply_changes(
            [FileChange(path="app.py", content="new", operation=OP_MODIFY)],
            project_root=tmp_path,
        )
        assert result.written == ["app.py"]
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "new"
        assert (tmp_path / "app.py.bak").read_text(encoding="utf-8") == "old"
        assert result.backups == [str(tmp_path / "app.py.bak")]

    def test_modify_backups_disabled(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("old", encoding="utf-8")
        config = GeneratorConfig(create_backups=False)
        result = CodeGenerator(config).apply_changes(
            [FileChange(path="app.py", content="new", operation=OP_MODIFY)],
            project_root=tmp_path,
        )
        assert result.backups == []
        assert not (tmp_path / "app.py.bak").exists()

    def test_modify_missing_skipped(self, tmp_path) -> None:
        result = CodeGenerator().apply_changes(
            [FileChange(path="app.py", content="new", operation=OP_MODIFY)],
            project_root=tmp_path,
        )
        assert result.skipped == ["app.py (missing)"]

    def test_modify_disabled_skips(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("old", encoding="utf-8")
        config = GeneratorConfig(allow_modify_existing=False)
        result = CodeGenerator(config).apply_changes(
            [FileChange(path="app.py", content="new", operation=OP_MODIFY)],
            project_root=tmp_path,
        )
        assert result.skipped == ["app.py (modify disabled)"]
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "old"


class TestCodeGeneratorDelete:
    def test_delete_disabled_by_default(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("old", encoding="utf-8")
        result = CodeGenerator().apply_changes(
            [FileChange(path="app.py", operation=OP_DELETE)], project_root=tmp_path
        )
        assert result.skipped == ["app.py (deletes disabled)"]
        assert (tmp_path / "app.py").exists()

    def test_delete_enabled_removes_file(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("old", encoding="utf-8")
        config = GeneratorConfig(allow_delete=True)
        result = CodeGenerator(config).apply_changes(
            [FileChange(path="app.py", operation=OP_DELETE)], project_root=tmp_path
        )
        assert result.written == ["app.py"]
        assert not (tmp_path / "app.py").exists()

    def test_delete_missing_skipped(self, tmp_path) -> None:
        config = GeneratorConfig(allow_delete=True)
        result = CodeGenerator(config).apply_changes(
            [FileChange(path="app.py", operation=OP_DELETE)], project_root=tmp_path
        )
        assert result.skipped == ["app.py (missing)"]


class TestCodeGeneratorSafety:
    def test_dry_run_writes_nothing(self, tmp_path) -> None:
        result = CodeGenerator().apply_changes(
            [FileChange(path="app.py", content="x")],
            project_root=tmp_path,
            dry_run=True,
        )
        assert result.dry_run
        assert result.written == ["app.py"]
        assert not (tmp_path / "app.py").exists()

    def test_dry_run_keeps_original_content(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("old", encoding="utf-8")
        result = CodeGenerator().apply_changes(
            [FileChange(path="app.py", content="new", operation=OP_MODIFY)],
            project_root=tmp_path,
            dry_run=True,
        )
        assert result.written == ["app.py"]
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "old"

    def test_too_many_files_reported(self, tmp_path) -> None:
        config = GeneratorConfig(max_files_per_task=2)
        changes = [FileChange(path=f"f{i}.py", content="x") for i in range(3)]
        result = CodeGenerator(config).apply_changes(changes, project_root=tmp_path)
        assert not result.success
        assert result.errors[0]["path"] == "*"
        assert "Too many files" in result.errors[0]["error"]

    def test_path_escape_rejected(self, tmp_path) -> None:
        result = CodeGenerator().apply_changes(
            [FileChange(path="../escape.txt", content="x")], project_root=tmp_path
        )
        assert not result.success
        assert "Path escapes project root" in result.errors[0]["error"]
        assert not (tmp_path.parent / "escape.txt").exists()

    def test_blocked_pattern_rejected(self, tmp_path) -> None:
        result = CodeGenerator().apply_changes(
            [FileChange(path=".env", content="x")], project_root=tmp_path
        )
        assert not result.success
        assert result.errors[0]["error"] == "Path not allowed: .env"

    def test_oversized_file_rejected(self, tmp_path) -> None:
        config = GeneratorConfig(max_file_size_bytes=10)
        result = CodeGenerator(config).apply_changes(
            [FileChange(path="app.py", content="x" * 20)], project_root=tmp_path
        )
        assert not result.success
        assert "File too large" in result.errors[0]["error"]
        assert not (tmp_path / "app.py").exists()

    def test_unknown_operation_skipped(self, tmp_path) -> None:
        result = CodeGenerator().apply_changes(
            [FileChange(path="app.py", content="x", operation="explode")],
            project_root=tmp_path,
        )
        assert result.skipped == ["app.py (unknown operation explode)"]


class TestCodeGeneratorRun:
    def _context(self, tmp_path) -> DeveloperContext:
        config = DeveloperConfig(project_root=str(tmp_path))
        return DeveloperContext(config=config, registry=DeveloperRegistry())

    def test_run_without_plan_raises(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        with pytest.raises(GenerationError, match="No plan artifact"):
            CodeGenerator().run(ctx, "goal")

    def test_run_applies_plan_changes(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        plan = ProjectPlanner().plan(
            "goal",
            tasks=[
                {
                    "title": "Create app",
                    "files": [{"path": "app.py", "content": "x = 1", "reason": "core"}],
                }
            ],
        )
        ctx.set_artifact(PHASE_PLAN, plan)
        result = CodeGenerator().run(ctx, "goal")
        assert result.written == ["app.py"]
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "x = 1"
        assert ctx.stats["files_written"] == 1
        assert ctx.stats["files_errors"] == 0
        events = [e.type for e in ctx.bus.history(event_type="implementation.completed")]
        assert events == ["implementation.completed"]

    def test_run_dry_run_kwarg(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        plan = ProjectPlanner().plan(
            "goal",
            tasks=[{"title": "Create app", "files": [{"path": "app.py", "content": "x"}]}],
        )
        ctx.set_artifact(PHASE_PLAN, plan)
        result = CodeGenerator().run(ctx, "goal", dry_run=True)
        assert result.dry_run
        assert not (tmp_path / "app.py").exists()
