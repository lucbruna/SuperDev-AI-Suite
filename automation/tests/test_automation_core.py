"""Smoke tests for the automation core (Volume 20, Fase 1)."""

from __future__ import annotations

from typing import Any

import pytest

from automation.automation_config import AutomationConfig
from automation.automation_context import AutomationContext
from automation.automation_engine import AutomationEngine
from automation.automation_events import AutomationEventType, AutomationEvents
from automation.automation_factory import AutomationFactory
from automation.automation_manager import AutomationManager
from automation.automation_metrics import AutomationMetrics
from automation.automation_models import (AutomationResult, ExecutionRecord,
                                          ScheduleSpec, TaskRecord, TriggerSpec,
                                          TriggerType, WorkflowDefinition,
                                          WorkflowStatus, WorkflowStep)
from automation.automation_protocols import (coerce_bool, coerce_number,
                                             new_id, safe_get)
from automation.automation_registry import AutomationRegistry
from automation.automation_runtime import AutomationRuntime
from automation.automation_security import AutomationSecurity


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------
class TestAutomationConfig:
    def test_defaults(self) -> None:
        config = AutomationConfig()
        assert config.max_retries == 3
        assert config.security_level == "standard"
        assert config.workspace == "default"

    def test_merge_overrides(self) -> None:
        config = AutomationConfig(workspace="store-a")
        merged = config.merge(max_retries=5, settings={"region": "br"})
        assert merged.max_retries == 5
        assert merged.workspace == "store-a"
        assert merged.settings["region"] == "br"
        # original untouched
        assert config.max_retries == 3

    def test_to_dict(self) -> None:
        data = AutomationConfig().to_dict()
        assert data["max_retries"] == 3
        assert "security_level" in data


# ---------------------------------------------------------------------------
# models
# ---------------------------------------------------------------------------
class TestAutomationModels:
    def test_workflow_status_values(self) -> None:
        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.FAILED.value == "failed"

    def test_trigger_type_values(self) -> None:
        assert TriggerType.EVENT.value == "event"
        assert TriggerType.CONDITION.value == "condition"

    def test_workflow_definition_to_dict(self) -> None:
        workflow = WorkflowDefinition(
            workflow_id="wf-1",
            name="Reabastecimento",
            steps=[WorkflowStep(step_id="s1", action="stock.check")],
            tags=["estoque"],
        )
        data = workflow.to_dict()
        assert data["workflow_id"] == "wf-1"
        assert data["steps"][0]["action"] == "stock.check"
        assert data["triggers"] == []
        assert data["active"] is True

    def test_execution_record_to_dict(self) -> None:
        record = ExecutionRecord(
            execution_id="exec-1", workflow_id="wf-1",
            status=WorkflowStatus.COMPLETED, steps_completed=2,
            result={"ok": True},
        )
        data = record.to_dict()
        assert data["status"] == "completed"
        assert data["steps_completed"] == 2

    def test_automation_result(self) -> None:
        result = AutomationResult(True, result={"done": True})
        assert result.success is True
        assert result.to_dict()["success"] is True

    def test_trigger_and_schedule_specs(self) -> None:
        trigger = TriggerSpec("t1", TriggerType.DATABASE, {"table": "orders"})
        assert trigger.enabled is True
        schedule = ScheduleSpec("sch-1", "wf-1", cron="0 8 * * *")
        assert schedule.cron == "0 8 * * *"
        assert schedule.enabled is True

    def test_task_record(self) -> None:
        task = TaskRecord("task-1", "wf-1", "s1", "agent.run")
        assert task.status == WorkflowStatus.PENDING
        assert task.error is None


# ---------------------------------------------------------------------------
# events
# ---------------------------------------------------------------------------
class TestAutomationEvents:
    def test_publish_and_listen(self) -> None:
        events = AutomationEvents()
        seen: list[dict[str, str]] = []
        events.on(AutomationEventType.WORKFLOW_STARTED, lambda d: seen.append(d))
        events.publish(AutomationEventType.WORKFLOW_STARTED, {"execution_id": "e1"})
        assert len(seen) == 1
        assert seen[0]["type"] == "workflow.started"
        assert seen[0]["execution_id"] == "e1"

    def test_once_fires_single_time(self) -> None:
        events = AutomationEvents()
        count = [0]
        events.once(AutomationEventType.TRIGGER_FIRED, lambda d: count.__setitem__(0, count[0] + 1))
        events.publish(AutomationEventType.TRIGGER_FIRED)
        events.publish(AutomationEventType.TRIGGER_FIRED)
        assert count[0] == 1

    def test_off_removes_listener(self) -> None:
        events = AutomationEvents()
        count = [0]

        def listener(data: dict[str, str]) -> None:
            count[0] += 1

        events.on(AutomationEventType.TASK_COMPLETED, listener)
        events.publish(AutomationEventType.TASK_COMPLETED)
        events.off(AutomationEventType.TASK_COMPLETED, listener)
        events.publish(AutomationEventType.TASK_COMPLETED)
        assert count[0] == 1
        assert events.listener_count(AutomationEventType.TASK_COMPLETED) == 0

    def test_listener_exception_is_isolated(self) -> None:
        events = AutomationEvents()
        seen = []

        def boom(_: dict[str, str]) -> None:
            raise RuntimeError("boom")

        events.on(AutomationEventType.WORKFLOW_FAILED, boom)
        events.on(AutomationEventType.WORKFLOW_FAILED, lambda d: seen.append(d))
        events.publish(AutomationEventType.WORKFLOW_FAILED)
        assert len(seen) == 1


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------
class TestAutomationMetrics:
    def test_increment_and_counter(self) -> None:
        metrics = AutomationMetrics()
        metrics.increment("tasks.completed")
        metrics.increment("tasks.completed")
        metrics.increment("executions.started")
        assert metrics.counter("tasks.completed") == 2
        assert metrics.counter("missing") == 0

    def test_timing_and_average(self) -> None:
        metrics = AutomationMetrics()
        metrics.record_timing("step.run", 0.2)
        metrics.record_timing("step.run", 0.4)
        assert pytest.approx(metrics.average("step.run")) == 0.3
        assert metrics.count_timings("step.run") == 2
        assert metrics.average("absent") == 0.0

    def test_time_block_context(self) -> None:
        metrics = AutomationMetrics()
        with metrics.time_block("workflow.run"):
            pass
        assert metrics.count_timings("workflow.run") == 1
        assert metrics.average("workflow.run") >= 0.0

    def test_snapshot(self) -> None:
        metrics = AutomationMetrics()
        metrics.increment("executions.completed", 3)
        metrics.record_timing("step.run", 0.5)
        snap = metrics.snapshot()
        assert snap["counters"]["executions.completed"] == 3
        assert snap["averages"]["step.run"] == 0.5


# ---------------------------------------------------------------------------
# security
# ---------------------------------------------------------------------------
class TestAutomationSecurity:
    def test_redact_sensitive_keys(self) -> None:
        data = AutomationSecurity.redact({
            "user": "ana",
            "password": "1234",
            "token": "abc",
            "safe": "value",
        })
        assert data["password"] == "***"
        assert data["token"] == "***"
        assert data["user"] == "ana"
        assert data["safe"] == "value"

    def test_redact_nested(self) -> None:
        data = AutomationSecurity.redact({"auth": {"api_key": "xyz", "region": "br"}})
        assert data["auth"]["api_key"] == "***"
        assert data["auth"]["region"] == "br"

    def test_sanitize_name(self) -> None:
        assert AutomationSecurity.sanitize_name("  Relatório  Diário  ") == "Relat-rio-Di-rio"
        assert AutomationSecurity.sanitize_name("a--b") == "a-b"

    def test_validate_payload(self) -> None:
        assert AutomationSecurity.validate_payload({"a": 1}) == []
        assert AutomationSecurity.validate_payload("nope") == ["payload must be a dict"]

    def test_restrict_actions(self) -> None:
        security = AutomationSecurity()
        assert security.can_execute("anything") is True
        security.restrict_actions(["stock.check", "email.send"])
        assert security.can_execute("stock.check") is True
        assert security.can_execute("agent.run") is False


# ---------------------------------------------------------------------------
# context
# ---------------------------------------------------------------------------
class TestAutomationContext:
    def test_set_get_and_records(self) -> None:
        context = AutomationContext("wf-1", {"initial": 1})
        context.set("stock", 12)
        assert context.get("stock") == 12
        assert context.get("initial") == 1
        assert context.get("missing", "x") == "x"

        context.record_step("s1", {"quantity": 12})
        assert context.step_result("s1") == {"quantity": 12}
        data = context.to_dict()
        assert data["workflow_id"] == "wf-1"
        assert data["attributes"]["stock"] == 12


# ---------------------------------------------------------------------------
# protocols
# ---------------------------------------------------------------------------
class TestAutomationProtocols:
    def test_new_id_prefix(self) -> None:
        assert new_id("wf").startswith("wf-")

    def test_safe_get_dot_path(self) -> None:
        data = {"store": {"stock": {"sku-1": 5}}}
        assert safe_get(data, "store.stock.sku-1") == 5
        assert safe_get(data, "store.missing", 0) == 0
        assert safe_get(data, "x.y.z", None) is None

    def test_coerce_bool(self) -> None:
        assert coerce_bool("true") is True
        assert coerce_bool("sim") is True
        assert coerce_bool("1") is True
        assert coerce_bool("não") is False
        assert coerce_bool(0) is False

    def test_coerce_number(self) -> None:
        assert coerce_number("1.5") == 1.5
        assert coerce_number("1,75") == 1.75
        assert coerce_number(3) == 3.0


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------
class TestAutomationRegistry:
    def test_workflow_crud(self) -> None:
        registry = AutomationRegistry()
        workflow = WorkflowDefinition("wf-1", "Teste")
        registry.register_workflow(workflow)
        assert registry.get_workflow("wf-1") is workflow
        assert registry.list_workflows() == ["wf-1"]
        assert registry.remove_workflow("wf-1") is True
        assert registry.remove_workflow("wf-1") is False

    def test_triggers_schedules_actions(self) -> None:
        registry = AutomationRegistry()
        registry.register_trigger("t1", "event", {"source": "erp"})
        trigger = registry.get_trigger("t1")
        assert trigger is not None
        assert trigger["type"] == "event"
        registry.register_schedule(ScheduleSpec("sch-1", "wf-1"))
        schedule = registry.get_schedule("sch-1")
        assert schedule is not None
        assert schedule.cron == "0 8 * * *"

        def handler(_: dict[str, object]) -> str:
            return "ok"

        registry.register_action("stock.check", handler)
        assert registry.has_action("stock.check") is True
        assert registry.get_action("stock.check") is handler
        assert registry.list_actions() == ["stock.check"]

    def test_snapshot(self) -> None:
        registry = AutomationRegistry()
        registry.register_workflow(WorkflowDefinition("wf-1", "Teste"))
        snap = registry.snapshot()
        assert snap["workflows"] == 1
        assert snap["triggers"] == 0


# ---------------------------------------------------------------------------
# engine (factory + manager + runtime + facade)
# ---------------------------------------------------------------------------
class TestAutomationEngine:
    def _build_engine(self, **overrides: object) -> AutomationEngine:
        return AutomationFactory().build_engine(**overrides)

    def test_factory_builds_wired_engine(self) -> None:
        engine = self._build_engine(workspace="store-a")
        assert engine.is_running() is False
        engine.initialize()
        assert engine.is_running() is True
        # idempotent start
        engine.initialize()
        assert engine.is_running() is True
        engine.shutdown()
        assert engine.is_running() is False

    def test_engine_executes_successful_workflow(self) -> None:
        engine = self._build_engine()
        engine.register_action("stock.check",
                               lambda p: {"stock": p.get("sku", "x") == "sku-1"})
        engine.register_action("order.create",
                               lambda p: {"order_id": "pedido-1"})
        workflow = WorkflowDefinition(
            workflow_id="wf-reabastecer",
            name="Reabastecer",
            steps=[
                WorkflowStep("s1", "stock.check"),
                WorkflowStep("s2", "order.create"),
            ],
        )
        engine.create_workflow(workflow)
        result = engine.execute("wf-reabastecer", {"sku": "sku-1"})
        assert result.success is True
        assert "execution_id" in result.result
        record = engine.manager.get_execution(result.result["execution_id"])
        assert record is not None
        assert record.status == WorkflowStatus.COMPLETED
        assert engine.stats()["registry"]["workflows"] == 1
        assert engine.stats()["metrics"]["counters"]["executions.completed"] == 1

    def test_engine_fails_on_unknown_workflow(self) -> None:
        engine = self._build_engine()
        result = engine.execute("missing")
        assert result.success is False
        assert "not found" in (result.error or "")

    def test_engine_fails_on_inactive_workflow(self) -> None:
        engine = self._build_engine()
        engine.create_workflow(WorkflowDefinition(
            "wf-off", "Off", active=False,
            steps=[WorkflowStep("s1", "anything")]))
        result = engine.execute("wf-off")
        assert result.success is False
        assert "inactive" in (result.error or "")

    def test_engine_fails_on_missing_handler(self) -> None:
        engine = self._build_engine()
        engine.create_workflow(WorkflowDefinition(
            "wf-no-handler", "Sem handler",
            steps=[WorkflowStep("s1", "ghost.action")]))
        result = engine.execute("wf-no-handler")
        assert result.success is False
        assert "no handler" in (result.error or "")

    def test_engine_blocks_disallowed_action(self) -> None:
        factory = AutomationFactory()
        engine = factory.build_engine()
        engine.security.restrict_actions(["safe.action"])
        engine.create_workflow(WorkflowDefinition(
            "wf-danger", "Danger",
            steps=[WorkflowStep("s1", "drop.database")]))
        result = engine.execute("wf-danger")
        assert result.success is False
        assert "not allowed" in (result.error or "")

    def test_engine_workflow_state_chains_steps(self) -> None:
        engine = self._build_engine()
        engine.register_action("agent.planner", lambda p: {"tasks": ["codar", "testar"]})
        engine.register_action("agent.developer", lambda p: {"code_written": True})
        engine.create_workflow(WorkflowDefinition(
            "wf-dev", "Pipeline dev",
            steps=[
                WorkflowStep("s1", "agent.planner"),
                WorkflowStep("s2", "agent.developer",
                             params={"task": "codar"}),
            ],
        ))
        result = engine.execute("wf-dev")
        assert result.success is True
        assert result.result["attributes"]["tasks"] == ["codar", "testar"]
        assert result.result["attributes"]["code_written"] is True

    def test_engine_triggers_and_schedules(self) -> None:
        engine = self._build_engine()
        fired = [False]
        engine.register_trigger(
            TriggerSpec("t-low-stock", TriggerType.CONDITION, {"sku": "sku-1"}),
            lambda event: event.get("stock", 999) < 10)
        engine.fire_trigger("t-low-stock", {"stock": 4})
        # direct evaluation stored per-trigger: use callback via closure
        def mark_fired(_: dict[str, Any]) -> bool:
            fired[0] = True
            return True

        engine.register_trigger(TriggerSpec("t-cb", TriggerType.EVENT, {}), mark_fired)
        assert engine.fire_trigger("t-cb", {"any": 1}) is True
        assert fired[0] is True

        schedule = ScheduleSpec("sch-diario", "wf-dev", cron="0 8 * * *")
        engine.register_schedule(schedule)
        assert engine.registry.get_schedule("sch-diario") is schedule
        assert engine.list_workflows() == []
        assert engine.stats()["registry"]["schedules"] == 1

    def test_execution_history(self) -> None:
        engine = self._build_engine()
        engine.register_action("ping", lambda p: {"pong": True})
        engine.create_workflow(WorkflowDefinition(
            "wf-ping", "Ping",
            steps=[WorkflowStep("s1", "ping")]))
        engine.execute("wf-ping")
        executions = engine.manager.list_executions()
        assert len(executions) == 1
        assert executions[0]["status"] == "completed"
