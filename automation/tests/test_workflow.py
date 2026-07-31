"""Tests for the workflow subsystem (Volume 20, Fase 2)."""

from __future__ import annotations

import time
from typing import Any

import pytest

from automation.automation_events import AutomationEventType, AutomationEvents
from automation.automation_metrics import AutomationMetrics
from automation.automation_models import WorkflowStatus, WorkflowStep
from automation.workflow.workflow_builder import WorkflowBuilder
from automation.workflow.workflow_engine import WorkflowEngine
from automation.workflow.workflow_executor import WorkflowExecutor
from automation.workflow.workflow_manager import WorkflowManager
from automation.workflow.workflow_state import WorkflowState
from automation.workflow.workflow_validator import WorkflowValidator
from automation.workflow.workflow_version import WorkflowVersioner


# ---------------------------------------------------------------------------
# builder
# ---------------------------------------------------------------------------
class TestWorkflowBuilder:
    def test_build_definition(self) -> None:
        workflow = (WorkflowBuilder()
                    .id("wf-pedido")
                    .name("Processar Pedido")
                    .description("Fluxo de compra")
                    .step("validar-pagamento", "payment.validate",
                          params={"gateway": "stripe"})
                    .step("verificar-estoque", "stock.check")
                    .trigger("t-pedido")
                    .tag("compras")
                    .build())
        assert workflow.workflow_id == "wf-pedido"
        assert workflow.name == "Processar Pedido"
        assert len(workflow.steps) == 2
        assert workflow.steps[0].params["gateway"] == "stripe"
        assert workflow.triggers == ["t-pedido"]
        assert workflow.tags == ["compras"]
        assert workflow.version == "1.0.0"


# ---------------------------------------------------------------------------
# validator
# ---------------------------------------------------------------------------
class TestWorkflowValidator:
    def _valid(self) -> Any:
        return (WorkflowBuilder()
                .id("wf-1").name("Valido")
                .step("s1", "stock.check")
                .build())

    def test_valid_workflow(self) -> None:
        assert WorkflowValidator().validate(self._valid()) == []

    def test_missing_id_and_name(self) -> None:
        workflow = WorkflowBuilder().name("Sem id").build()
        issues = WorkflowValidator().validate(workflow)
        assert "workflow_id is required" in issues

    def test_no_steps(self) -> None:
        workflow = WorkflowBuilder().id("wf-1").name("Vazio").build()
        assert "workflow has no steps" in WorkflowValidator().validate(workflow)

    def test_duplicate_step_ids(self) -> None:
        workflow = (WorkflowBuilder().id("wf-1").name("Duplicado")
                    .step("s1", "a").step("s1", "b").build())
        assert "duplicate step_ids detected" in WorkflowValidator().validate(workflow)

    def test_empty_action(self) -> None:
        workflow = (WorkflowBuilder().id("wf-1").name("Sem acao")
                    .step("s1", "").build())
        assert "step 's1' has no action" in WorkflowValidator().validate(workflow)

    def test_dangling_transitions(self) -> None:
        workflow = (WorkflowBuilder().id("wf-1").name("Dangling")
                    .step("s1", "a", next_on_success="ghost",
                          next_on_failure="boo")
                    .build())
        issues = WorkflowValidator().validate(workflow)
        assert any("next_on_success" in i and "ghost" in i for i in issues)
        assert any("next_on_failure" in i and "boo" in i for i in issues)


# ---------------------------------------------------------------------------
# executor
# ---------------------------------------------------------------------------
class TestWorkflowExecutor:
    def _linear_workflow(self) -> Any:
        return (WorkflowBuilder().id("wf-linear").name("Linear")
                .step("s1", "alpha")
                .step("s2", "beta")
                .step("s3", "gamma")
                .build())

    def test_linear_success(self) -> None:
        executor = WorkflowExecutor()
        calls: list[str] = []
        executor.register_action("alpha", lambda p: calls.append("a") or {})
        executor.register_action("beta", lambda p: calls.append("b") or {})
        executor.register_action("gamma", lambda p: calls.append("c") or {})
        state = executor.run(self._linear_workflow())
        assert calls == ["a", "b", "c"]
        assert state.status == WorkflowStatus.COMPLETED
        assert state.completed_steps == ["s1", "s2", "s3"]
        assert state.failed_steps == []
        assert state.error is None
        assert state.finished_at is not None

    def test_variables_propagate(self) -> None:
        executor = WorkflowExecutor()
        executor.register_action("set.qty", lambda p: {"qty": 12})
        executor.register_action("check.qty", lambda p: {"ok": p["qty"] == 12})
        workflow = (WorkflowBuilder().id("wf-vars").name("Vars")
                    .step("s1", "set.qty").step("s2", "check.qty").build())
        state = executor.run(workflow)
        assert state.variables["ok"] is True

    def test_next_on_success_branch(self) -> None:
        executor = WorkflowExecutor()
        calls: list[str] = []
        executor.register_action("skip.me", lambda p: calls.append("skip") or {})
        executor.register_action("do.now", lambda p: calls.append("do") or {})
        workflow = (WorkflowBuilder().id("wf-branch").name("Branch")
                    .step("s1", "skip.me", next_on_success="s3")
                    .step("s2", "do.now")
                    .step("s3", "do.now")
                    .build())
        state = executor.run(workflow)
        # s2 is skipped because s1 jumps to s3
        assert calls == ["skip", "do"]
        assert state.completed_steps == ["s1", "s3"]

    def test_failure_uses_next_on_failure(self) -> None:
        executor = WorkflowExecutor()
        calls: list[str] = []

        def fail(_: dict[str, Any]) -> None:
            calls.append("fail")
            raise ValueError("pagamento recusado")

        executor.register_action("payment.validate", fail)
        executor.register_action("order.cancel",
                                 lambda p: calls.append("cancel") or {})
        workflow = (WorkflowBuilder().id("wf-fail").name("Falha")
                    .step("validar", "payment.validate", next_on_failure="cancelar")
                    .step("notificar", "order.cancel")
                    .step("cancelar", "order.cancel")
                    .build())
        state = executor.run(workflow, {"order": "pedido-9"})
        assert state.status == WorkflowStatus.COMPLETED
        assert state.failed_steps == ["validar"]
        assert calls == ["fail", "cancel"]
        assert "recusado" in (state.error or "")

    def test_failure_without_branch_stops(self) -> None:
        executor = WorkflowExecutor()
        executor.register_action("boom", lambda p: (_ for _ in ()).throw(
            RuntimeError("falha total")))
        workflow = (WorkflowBuilder().id("wf-stop").name("Para")
                    .step("s1", "boom").step("s2", "never").build())
        state = executor.run(workflow)
        assert state.status == WorkflowStatus.FAILED
        assert state.completed_steps == []
        assert state.failed_steps == ["s1"]
        assert "falha total" in (state.error or "")

    def test_missing_handler(self) -> None:
        workflow = (WorkflowBuilder().id("wf-noh").name("Sem handler")
                    .step("s1", "ghost.action").build())
        state = WorkflowExecutor().run(workflow)
        assert state.status == WorkflowStatus.FAILED
        assert "no handler" in (state.error or "")

    def test_timeout_exceeded(self) -> None:
        executor = WorkflowExecutor()

        def slow(_: dict[str, Any]) -> dict[str, Any]:
            time.sleep(0.05)
            return {"done": True}

        executor.register_action("slow", slow)
        workflow = (WorkflowBuilder().id("wf-timeout").name("Timeout")
                    .step("s1", "slow", timeout=0.01, next_on_failure="fallback")
                    .step("fallback", "slow")
                    .build())
        state = executor.run(workflow)
        assert state.status == WorkflowStatus.COMPLETED
        assert state.failed_steps == ["s1"]
        assert "timeout" in (state.error or "")

    def test_cycle_detection(self) -> None:
        executor = WorkflowExecutor()
        executor.register_action("loop", lambda p: {})
        workflow = (WorkflowBuilder().id("wf-cycle").name("Ciclo")
                    .step("s1", "loop", next_on_success="s2")
                    .step("s2", "loop", next_on_success="s1")
                    .build())
        state = executor.run(workflow)
        assert state.status == WorkflowStatus.FAILED
        assert "cycle" in (state.error or "")

    def test_events_and_metrics_wired(self) -> None:
        events = AutomationEvents()
        metrics = AutomationMetrics()
        executor = WorkflowExecutor(events=events, metrics=metrics)
        completed: list[str] = []
        events.on(AutomationEventType.WORKFLOW_COMPLETED,
                  lambda d: completed.append(d["workflow_id"]))
        executor.register_action("ping", lambda p: {})
        workflow = (WorkflowBuilder().id("wf-ev").name("Eventos")
                    .step("s1", "ping").build())
        state = executor.run(workflow)
        assert state.status == WorkflowStatus.COMPLETED
        assert completed == ["wf-ev"]
        assert metrics.counter("tasks.completed") == 1
        assert metrics.counter("workflows.started") == 1


# ---------------------------------------------------------------------------
# manager + versioner
# ---------------------------------------------------------------------------
class TestWorkflowManager:
    def test_register_rejects_invalid(self) -> None:
        manager = WorkflowManager()
        workflow = (WorkflowBuilder().id("wf-bad").name("Ruim")
                    .step("s1", "").build())
        issues = manager.register(workflow)
        assert issues is not None
        assert "has no action" in issues[0]
        assert manager.list() == []

    def test_register_and_run(self) -> None:
        manager = WorkflowManager()
        manager.register_action("ping", lambda p: {"pong": True})
        workflow = (WorkflowBuilder().id("wf-mgr").name("Gerente")
                    .step("s1", "ping").build())
        assert manager.register(workflow) is None
        state = manager.run("wf-mgr")
        assert state is not None
        assert state.status == WorkflowStatus.COMPLETED
        assert len(manager.history()) == 1

    def test_run_unknown_returns_none(self) -> None:
        assert WorkflowManager().run("missing") is None

    def test_remove(self) -> None:
        manager = WorkflowManager()
        manager.register((WorkflowBuilder().id("wf-rm").name("Remover")
                          .step("s1", "ping").build()))
        assert manager.remove("wf-rm") is True
        assert manager.remove("wf-rm") is False

    def test_versioner_increments(self) -> None:
        versioner = WorkflowVersioner()
        definition = (WorkflowBuilder().id("wf-v").name("Versao")
                      .step("s1", "ping").build())
        assert versioner.register(definition) == "1.0.0"
        assert versioner.version_of("wf-v") == "1.0.0"
        assert versioner.register(definition) == "1.0.1"
        assert versioner.register(definition) == "1.0.2"
        assert len(versioner.history("wf-v")) == 3
        stored = versioner.get("wf-v", "1.0.1")
        assert stored is not None
        assert stored.workflow_id == "wf-v"


# ---------------------------------------------------------------------------
# engine facade + user example (validar pagamento -> verificar estoque ->
# gerar nota fiscal -> enviar entrega)
# ---------------------------------------------------------------------------
class TestWorkflowEngine:
    def test_full_purchase_flow(self) -> None:
        engine = WorkflowEngine()

        def validate_payment(params: dict[str, Any]) -> dict[str, Any]:
            assert params["gateway"] == "stripe"
            return {"payment": "approved", "customer": "ana"}

        engine.register_action("payment.validate", validate_payment)
        engine.register_action("stock.check",
                               lambda p: {"in_stock": True})
        engine.register_action("invoice.generate",
                               lambda p: {"invoice_id": "NF-2026-0001"})
        engine.register_action("delivery.send",
                               lambda p: {"tracking": "BR-987654"})

        workflow = (engine.build()
                    .id("wf-pedido")
                    .name("Processar Pedido")
                    .description("Validar pagamento -> verificar estoque -> "
                                 "gerar nota fiscal -> enviar entrega")
                    .step("validar-pagamento", "payment.validate",
                          params={"gateway": "stripe"})
                    .step("verificar-estoque", "stock.check")
                    .step("gerar-nota", "invoice.generate")
                    .step("enviar-entrega", "delivery.send")
                    .tag("compras")
                    .build())
        assert engine.register(workflow) is None

        state = engine.run("wf-pedido", {"order_id": "pedido-1"})
        assert state is not None
        assert state.status == WorkflowStatus.COMPLETED
        assert state.completed_steps == [
            "validar-pagamento", "verificar-estoque",
            "gerar-nota", "enviar-entrega"]
        assert state.variables["payment"] == "approved"
        assert state.variables["invoice_id"] == "NF-2026-0001"
        assert state.variables["tracking"] == "BR-987654"

        assert engine.version_of("wf-pedido") == "1.0.0"
        assert len(engine.versions("wf-pedido")) == 1
        assert len(engine.history()) == 1
        assert engine.get("wf-pedido") is not None

    def test_engine_validate_issue(self) -> None:
        engine = WorkflowEngine()
        workflow = (WorkflowBuilder().id("wf-x").name("X")
                    .step("s1", "a", next_on_success="missing")
                    .build())
        assert engine.validate(workflow) != []

    def test_payment_failure_cancels_order(self) -> None:
        engine = WorkflowEngine()

        def reject(_: dict[str, Any]) -> None:
            raise ValueError("cartao sem limite")

        engine.register_action("payment.validate", reject)
        engine.register_action("order.cancel",
                               lambda p: {"cancelled": True})
        workflow = (engine.build()
                    .id("wf-pedido-reprovado")
                    .name("Pedido Reprovado")
                    .step("validar-pagamento", "payment.validate",
                          next_on_failure="cancelar-pedido")
                    .step("cancelar-pedido", "order.cancel")
                    .build())
        assert engine.register(workflow) is None
        state = engine.run("wf-pedido-reprovado", {"order_id": "pedido-2"})
        assert state is not None
        assert state.status == WorkflowStatus.COMPLETED
        assert state.variables["cancelled"] is True
        assert state.failed_steps == ["validar-pagamento"]
        assert "limite" in (state.error or "")
