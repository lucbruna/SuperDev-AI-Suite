"""Tests for workflow module: base_workflow, condition_eval, workflow_manager."""

import pytest
from backend.workflow.base_workflow import (
    StepConfig,
    StepResult,
    StepStatus,
    StepType,
    WorkflowDefinition,
    WorkflowStatus,
)
from backend.workflow.condition_eval import safe_condition_eval


# ── WorkflowStatus / StepStatus / StepType Enums ────────────────────


class TestEnums:
    def test_workflow_status_values(self):
        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.RUNNING.value == "running"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"
        assert WorkflowStatus.PAUSED.value == "paused"
        assert WorkflowStatus.CANCELLED.value == "cancelled"

    def test_step_status_values(self):
        assert StepStatus.PENDING.value == "pending"
        assert StepStatus.RUNNING.value == "running"
        assert StepStatus.COMPLETED.value == "completed"
        assert StepStatus.FAILED.value == "failed"
        assert StepStatus.SKIPPED.value == "skipped"
        assert StepStatus.RETRYING.value == "retrying"

    def test_step_type_values(self):
        assert StepType.CODE.value == "code"
        assert StepType.API_CALL.value == "api_call"
        assert StepType.CONDITION.value == "condition"
        assert StepType.PARALLEL.value == "parallel"
        assert StepType.LOOP.value == "loop"
        assert StepType.HUMAN_APPROVAL.value == "human_approval"
        assert StepType.TRANSFORM.value == "transform"
        assert StepType.WAIT.value == "wait"


# ── StepConfig ──────────────────────────────────────────────────────


class TestStepConfig:
    def test_defaults(self):
        step = StepConfig(id="s1", name="Step 1", step_type=StepType.CODE)
        assert step.config == {}
        assert step.depends_on == []
        assert step.retry_count == 0
        assert step.max_retries == 3
        assert step.timeout_seconds == 300
        assert step.continue_on_error is False

    def test_custom_values(self):
        step = StepConfig(
            id="s1",
            name="Custom",
            step_type=StepType.CONDITION,
            config={"condition": "x > 5"},
            depends_on=["s0"],
            max_retries=5,
            timeout_seconds=60,
            continue_on_error=True,
        )
        assert step.config["condition"] == "x > 5"
        assert step.depends_on == ["s0"]
        assert step.max_retries == 5
        assert step.continue_on_error is True


# ── StepResult ──────────────────────────────────────────────────────


class TestStepResult:
    def test_defaults(self):
        result = StepResult(step_id="s1", status=StepStatus.COMPLETED)
        assert result.output is None
        assert result.error is None
        assert result.attempts == 0
        assert result.execution_time_ms == 0.0

    def test_with_error(self):
        result = StepResult(
            step_id="s1",
            status=StepStatus.FAILED,
            error="Something went wrong",
            attempts=3,
        )
        assert result.error == "Something went wrong"
        assert result.attempts == 3


# ── WorkflowDefinition ──────────────────────────────────────────────


class TestWorkflowDefinition:
    def test_get_step_found(self):
        step = StepConfig(id="s1", name="Step 1", step_type=StepType.CODE)
        wf = WorkflowDefinition(id="wf1", name="Test", steps=[step])
        assert wf.get_step("s1") is step

    def test_get_step_not_found(self):
        wf = WorkflowDefinition(id="wf1", name="Test")
        assert wf.get_step("nonexistent") is None

    def test_get_dependencies(self):
        step = StepConfig(
            id="s2", name="Step 2", step_type=StepType.CODE, depends_on=["s1"]
        )
        wf = WorkflowDefinition(id="wf1", name="Test", steps=[step])
        assert wf.get_dependencies("s2") == ["s1"]

    def test_get_dependencies_no_step(self):
        wf = WorkflowDefinition(id="wf1", name="Test")
        assert wf.get_dependencies("nonexistent") == []

    def test_get_root_steps(self):
        s1 = StepConfig(id="s1", name="Root", step_type=StepType.CODE)
        s2 = StepConfig(
            id="s2", name="Dep", step_type=StepType.CODE, depends_on=["s1"]
        )
        wf = WorkflowDefinition(id="wf1", name="Test", steps=[s1, s2])
        roots = wf.get_root_steps()
        assert len(roots) == 1
        assert roots[0].id == "s1"

    def test_validate_valid(self):
        s1 = StepConfig(id="s1", name="A", step_type=StepType.CODE)
        s2 = StepConfig(
            id="s2", name="B", step_type=StepType.CODE, depends_on=["s1"]
        )
        wf = WorkflowDefinition(id="wf1", name="Test", steps=[s1, s2])
        errors = wf.validate()
        assert errors == []

    def test_validate_missing_dependency(self):
        s1 = StepConfig(
            id="s1", name="A", step_type=StepType.CODE, depends_on=["missing"]
        )
        wf = WorkflowDefinition(id="wf1", name="Test", steps=[s1])
        errors = wf.validate()
        assert len(errors) == 1
        assert "missing" in errors[0]

    def test_validate_cycle_detection(self):
        s1 = StepConfig(id="s1", name="A", step_type=StepType.CODE, depends_on=["s2"])
        s2 = StepConfig(id="s2", name="B", step_type=StepType.CODE, depends_on=["s1"])
        wf = WorkflowDefinition(id="wf1", name="Test", steps=[s1, s2])
        errors = wf.validate()
        assert any("Cycle" in e for e in errors)

    def test_validate_empty_workflow(self):
        wf = WorkflowDefinition(id="wf1", name="Empty")
        errors = wf.validate()
        assert errors == []


# ── safe_condition_eval ─────────────────────────────────────────────


class TestSafeConditionEval:
    def test_simple_true(self):
        assert safe_condition_eval("True", {}) is True

    def test_simple_false(self):
        assert safe_condition_eval("False", {}) is False

    def test_comparison_gt(self):
        assert safe_condition_eval("x > 5", {"x": 10}) is True
        assert safe_condition_eval("x > 5", {"x": 3}) is False

    def test_comparison_lt(self):
        assert safe_condition_eval("x < 10", {"x": 5}) is True

    def test_comparison_eq(self):
        assert safe_condition_eval("x == 5", {"x": 5}) is True
        assert safe_condition_eval("x == 5", {"x": 6}) is False

    def test_comparison_ne(self):
        assert safe_condition_eval("x != 5", {"x": 6}) is True

    def test_comparison_lte(self):
        assert safe_condition_eval("x <= 5", {"x": 5}) is True
        assert safe_condition_eval("x <= 5", {"x": 6}) is False

    def test_comparison_gte(self):
        assert safe_condition_eval("x >= 5", {"x": 5}) is True
        assert safe_condition_eval("x >= 5", {"x": 4}) is False

    def test_arithmetic(self):
        # safe_condition_eval wraps result in bool(), so we test truthiness
        # For arithmetic, we need to test via comparisons
        assert safe_condition_eval("x + 1 == 6", {"x": 5}) is True
        assert safe_condition_eval("x * 2 == 10", {"x": 5}) is True
        assert safe_condition_eval("x - 1 == 4", {"x": 5}) is True
        assert safe_condition_eval("x / 2 == 5", {"x": 10}) is True
        assert safe_condition_eval("x // 3 == 3", {"x": 10}) is True
        assert safe_condition_eval("x % 3 == 1", {"x": 10}) is True
        assert safe_condition_eval("x ** 2 == 9", {"x": 3}) is True

    def test_unary_ops(self):
        assert safe_condition_eval("-x == -5", {"x": 5}) is True
        assert safe_condition_eval("+x == -5", {"x": -5}) is True

    def test_boolean_and(self):
        assert safe_condition_eval("True and True", {}) is True
        assert safe_condition_eval("True and False", {}) is False

    def test_boolean_or(self):
        assert safe_condition_eval("False or True", {}) is True
        assert safe_condition_eval("False or False", {}) is False

    def test_in_operator(self):
        assert safe_condition_eval("x in items", {"x": 1, "items": [1, 2, 3]}) is True
        assert safe_condition_eval("x in items", {"x": 4, "items": [1, 2, 3]}) is False

    def test_not_in_operator(self):
        assert safe_condition_eval("x not in items", {"x": 4, "items": [1, 2, 3]}) is True

    def test_is_operator(self):
        assert safe_condition_eval("x is None", {"x": None}) is True
        assert safe_condition_eval("x is not None", {"x": 5}) is True

    def test_string_constant(self):
        # safe_condition_eval wraps in bool(), non-empty string is truthy
        assert safe_condition_eval("'hello'", {}) is True
        assert safe_condition_eval("''", {}) is False

    def test_none_constant(self):
        # None is falsy
        assert safe_condition_eval("None", {}) is False

    def test_blocked_exec(self):
        with pytest.raises(ValueError, match="Function calls not allowed"):
            safe_condition_eval("exec('import os')", {})

    def test_blocked_eval(self):
        with pytest.raises(ValueError, match="Function calls not allowed"):
            safe_condition_eval("eval('1+1')", {})

    def test_blocked_open(self):
        with pytest.raises(ValueError, match="Function calls not allowed"):
            safe_condition_eval("open('file.txt')", {})

    def test_function_call_blocked(self):
        with pytest.raises(ValueError, match="Function calls not allowed"):
            safe_condition_eval("len([1,2,3])", {})

    def test_attribute_access_blocked(self):
        with pytest.raises(ValueError, match="Function calls not allowed"):
            safe_condition_eval("x.upper()", {"x": "hello"})

    def test_undefined_variable(self):
        with pytest.raises(NameError):
            safe_condition_eval("undefined_var", {})

    def test_unsupported_expression(self):
        with pytest.raises(ValueError, match="Unsupported expression"):
            safe_condition_eval("[1, 2, 3]", {})

    def test_chained_comparison(self):
        assert safe_condition_eval("1 < x < 10", {"x": 5}) is True
        assert safe_condition_eval("1 < x < 3", {"x": 5}) is False

    def test_complex_expression(self):
        ctx = {"age": 25, "active": True, "role": "admin"}
        assert safe_condition_eval("age >= 18 and active", ctx) is True
        assert safe_condition_eval("age < 18 or role == 'admin'", ctx) is True
