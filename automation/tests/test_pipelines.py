"""Tests for the pipelines subsystem (Volume 20, Fase 6)."""

from __future__ import annotations

import time

from automation.automation_events import AutomationEventType, AutomationEvents
from automation.automation_metrics import AutomationMetrics
from automation.pipelines.pipeline_builder import PipelineBuilder
from automation.pipelines.pipeline_engine import PipelineEngine
from automation.pipelines.pipeline_executor import PipelineExecutor
from automation.pipelines.pipeline_history import PipelineHistory
from automation.pipelines.pipeline_models import (
    PipelineDefinition,
    PipelineRun,
    PipelineStage,
    StageStatus,
)
from automation.pipelines.pipeline_validator import PipelineValidator


class TestPipelineModels:
    def test_to_dict(self) -> None:
        run = PipelineRun(run_id="run-1", pipeline_id="p-1",
                          status="completed")
        data = run.to_dict()
        assert data["run_id"] == "run-1"
        assert data["status"] == "completed"
        assert StageStatus.COMPLETED.value == "completed"


class TestPipelineBuilder:
    def test_build(self) -> None:
        pipeline = (PipelineBuilder()
                    .id("p-pedido").name("Pedido").on_failure("stop")
                    .stage("validar", "validate.payment")
                    .stage("nota", "note.generate")
                    .build())
        assert pipeline.pipeline_id == "p-pedido"
        assert [s.stage_id for s in pipeline.stages] == ["validar", "nota"]
        assert pipeline.on_failure == "stop"


class TestPipelineValidator:
    def _valid(self) -> PipelineDefinition:
        return (PipelineBuilder()
                .id("p-1").name("Válida")
                .stage("a", "action.a")
                .stage("b", "action.b", next_on_failure="a")
                .build())

    def test_valid(self) -> None:
        assert PipelineValidator().validate(self._valid()) == []

    def test_missing_id(self) -> None:
        pipeline = self._valid()
        pipeline.pipeline_id = ""
        assert any("pipeline_id" in i for i in PipelineValidator().validate(pipeline))

    def test_no_stages(self) -> None:
        pipeline = (PipelineBuilder().id("p-x").name("X").build())
        assert "pipeline has no stages" in PipelineValidator().validate(pipeline)

    def test_duplicate_stage_ids(self) -> None:
        pipeline = (PipelineBuilder().id("p-2").name("Dup")
                    .stage("a", "action.a").stage("a", "action.b")
                    .build())
        assert any("duplicate" in i for i in PipelineValidator().validate(pipeline))

    def test_unknown_ref(self) -> None:
        pipeline = (PipelineBuilder().id("p-3").name("Ref")
                    .stage("a", "action.a", next_on_success="ghost")
                    .build())
        assert any("unknown stage 'ghost'" in i
                   for i in PipelineValidator().validate(pipeline))

    def test_invalid_on_failure(self) -> None:
        pipeline = self._valid()
        pipeline.on_failure = "banana"
        assert any("on_failure" in i for i in PipelineValidator().validate(pipeline))


class TestPipelineExecutor:
    def _executor(self, actions=None) -> PipelineExecutor:
        return PipelineExecutor(actions=actions)

    def test_success_propagates_variables(self) -> None:
        executor = self._executor()
        executor.register_action("inc", lambda p: {"count": p.get("count", 0) + 1})
        pipeline = (PipelineBuilder().id("p-inc").name("Inc")
                    .stage("s1", "inc").stage("s2", "inc")
                    .build())
        run = executor.run(pipeline, {"count": 1})
        assert run.status == "completed"
        assert run.variables["count"] == 3
        assert run.stage_status == {"s1": "completed", "s2": "completed"}
        assert run.error is None

    def test_failure_skips_remaining(self) -> None:
        executor = self._executor()
        executor.register_action("ok", lambda p: {})
        pipeline = (PipelineBuilder().id("p-f").name("Fail")
                    .stage("s1", "ok").stage("s2", "no.handler")
                    .stage("s3", "ok")
                    .build())
        run = executor.run(pipeline)
        assert run.status == "failed"
        assert run.stage_status["s1"] == "completed"
        assert run.stage_status["s2"] == "failed"
        assert run.stage_status["s3"] == "skipped"
        assert "no.handler" in (run.error or "")

    def test_continue_on_failure(self) -> None:
        executor = self._executor()
        executor.register_action("ok", lambda p: {})
        pipeline = (PipelineBuilder().id("p-c").name("Continue")
                    .on_failure("continue")
                    .stage("s1", "no.handler").stage("s2", "ok")
                    .build())
        run = executor.run(pipeline)
        assert run.status == "completed"
        assert run.stage_status["s1"] == "failed"
        assert run.stage_status["s2"] == "completed"

    def test_next_on_failure_jump(self) -> None:
        executor = self._executor()
        executor.register_action("ok", lambda p: {})
        pipeline = (PipelineBuilder().id("p-j").name("Jump")
                    .stage("s1", "no.handler", next_on_failure="s3")
                    .stage("s2", "ok")
                    .stage("s3", "ok")
                    .build())
        run = executor.run(pipeline)
        assert run.status == "completed"
        assert run.stage_status["s1"] == "failed"
        assert run.stage_status["s2"] == "skipped"
        assert run.stage_status["s3"] == "completed"

    def test_timeout(self) -> None:
        executor = self._executor()

        def slow(_: dict[str, object]) -> dict[str, object]:
            time.sleep(0.05)
            return {}

        executor.register_action("slow", slow)
        pipeline = (PipelineBuilder().id("p-t").name("Timeout")
                    .stage("s1", "slow", timeout=0.001)
                    .build())
        run = executor.run(pipeline)
        assert run.status == "failed"
        assert "timeout" in (run.error or "")

    def test_events_and_metrics(self) -> None:
        events = AutomationEvents()
        metrics = AutomationMetrics()
        seen: list[str] = []
        events.on(AutomationEventType.TASK_COMPLETED,
                  lambda e: seen.append(e["stage_id"]))
        executor = PipelineExecutor(events=events, metrics=metrics)
        executor.register_action("ok", lambda p: {})
        pipeline = (PipelineBuilder().id("p-e").name("Events")
                    .stage("s1", "ok")
                    .build())
        run = executor.run(pipeline)
        assert run.status == "completed"
        assert seen == ["s1"]


class TestPipelineEngine:
    def test_register_and_run(self) -> None:
        engine = PipelineEngine()
        pipeline = (engine.build()
                    .id("p-reposicao").name("Reposição de estoque")
                    .stage("verificar", "stock.check", {"sku": "arroz"})
                    .stage("prever", "demand.forecast")
                    .stage("pedido", "order.create")
                    .stage("erp", "erp.update")
                    .build())
        assert engine.register(pipeline) is None
        assert engine.list() == ["p-reposicao"]
        calls: list[str] = []
        for action in ["stock.check", "demand.forecast",
                       "order.create", "erp.update"]:
            engine.register_action(action,
                                   lambda p, a=action: calls.append(a) or p)
        run = engine.run("p-reposicao", {"sku": "arroz"})
        assert run is not None
        assert run.status == "completed"
        assert calls == ["stock.check", "demand.forecast",
                         "order.create", "erp.update"]
        assert len(engine.run_history()) == 1
        assert engine.stats()["completed"] == 1
        assert engine.stats()["failed"] == 0

    def test_unknown_pipeline(self) -> None:
        assert PipelineEngine().run("ghost", {}) is None

    def test_invalid_pipeline_rejected(self) -> None:
        engine = PipelineEngine()
        pipeline = (engine.build().id("p-bad").name("Ruim")
                    .stage("s1", "action.a", next_on_success="ghost")
                    .build())
        issues = engine.register(pipeline)
        assert issues is not None
        assert "unknown stage 'ghost'" in issues[0]

    def test_remove(self) -> None:
        engine = PipelineEngine()
        pipeline = (engine.build().id("p-rm").name("Remover")
                    .stage("s1", "action.a")
                    .build())
        engine.register(pipeline)
        assert engine.remove("p-rm") is True
        assert engine.remove("p-rm") is False

    def test_failed_run_recorded_in_history(self) -> None:
        engine = PipelineEngine()
        pipeline = (engine.build().id("p-fail").name("Falha")
                    .stage("s1", "no.handler")
                    .build())
        engine.register(pipeline)
        run = engine.run("p-fail")
        assert run is not None and run.status == "failed"
        assert engine.stats()["failed"] == 1

    def test_user_example_supermarket_replenishment(self) -> None:
        """Exemplo real: reposição inteligente de supermercado.

        sistema verifica estoque -> IA analisa vendas históricas -> prevê
        demanda -> cria pedido fornecedor -> envia aprovação -> atualiza ERP.
        """
        engine = PipelineEngine()
        pipeline = (engine.build()
                    .id("p-supermercado").name("Reposição inteligente")
                    .description("Pipeline de reposição do supermercado")
                    .stage("verificar", "stock.check",
                           {"sku": "arroz", "min": 10})
                    .stage("analisar", "sales.analyze",
                           {"history_days": 30})
                    .stage("prever", "demand.forecast")
                    .stage("pedido", "order.create")
                    .stage("aprovar", "approval.send")
                    .stage("erp", "erp.update")
                    .build())
        engine.register(pipeline)
        log: list[str] = []
        handlers = {
            "stock.check": lambda p: {"stock": 4, "limit": p.get("min")},
            "sales.analyze": lambda p: {"sales_trend": "rising"},
            "demand.forecast": lambda p: {"forecast_qty": 120},
            "order.create": lambda p: {"order_id": "PO-2026-001"},
            "approval.send": lambda p: {"approval": "pending"},
            "erp.update": lambda p: {"erp_synced": True},
        }
        for action, handler in handlers.items():
            engine.register_action(action, handler)
        run = engine.run("p-supermercado", {"sku": "arroz"})
        assert run is not None and run.status == "completed"
        assert list(run.stage_status.values()) == ["completed"] * 6
        assert run.variables["order_id"] == "PO-2026-001"
        assert run.variables["erp_synced"] is True


class TestPipelineHistory:
    def test_count(self) -> None:
        history = PipelineHistory()
        history.record(PipelineRun(run_id="r1", pipeline_id="p",
                                   status="completed"))
        history.record(PipelineRun(run_id="r2", pipeline_id="p",
                                   status="failed"))
        assert history.count() == 2
        assert history.count("completed") == 1
        assert history.count("failed") == 1
