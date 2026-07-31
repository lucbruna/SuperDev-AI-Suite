"""Tests for the triggers subsystem (Volume 20, Fase 4)."""

from __future__ import annotations

from automation.automation_events import AutomationEventType, AutomationEvents
from automation.automation_metrics import AutomationMetrics
from automation.triggers.trigger_engine import TriggerEngine
from automation.triggers.trigger_evaluator import TriggerCondition, TriggerEvaluator
from automation.triggers.trigger_history import TriggerHistory
from automation.triggers.trigger_models import TriggerDefinition, TriggerEvent
from automation.triggers.trigger_registry import TriggerRegistry
from automation.triggers.trigger_router import TriggerRouter


class TestTriggerEvaluator:
    def test_comparison_ops(self) -> None:
        evaluator = TriggerEvaluator()
        assert evaluator.evaluate_condition({"field": "stock", "op": "lt", "value": 10},
                                            {"stock": 4}) is True
        assert evaluator.evaluate_condition({"field": "stock", "op": "lt", "value": 10},
                                            {"stock": 12}) is False
        assert evaluator.evaluate_condition({"field": "qty", "op": "gte", "value": 5},
                                            {"qty": 5}) is True
        assert evaluator.evaluate_condition({"field": "qty", "op": "ne", "value": 5},
                                            {"qty": 6}) is True

    def test_nested_dot_path(self) -> None:
        evaluator = TriggerEvaluator()
        data = {"store": {"stock": {"sku-1": 3}}}
        assert evaluator.evaluate_condition(
            {"field": "store.stock.sku-1", "op": "lt", "value": 10}, data) is True

    def test_combined_conditions(self) -> None:
        evaluator = TriggerEvaluator()
        condition = {
            "all": [
                {"field": "stock", "op": "lt", "value": 10},
                {"field": "priority", "op": "eq", "value": "alta"},
            ],
        }
        assert evaluator.evaluate_condition(condition,
                                            {"stock": 4, "priority": "alta"}) is True
        assert evaluator.evaluate_condition(condition,
                                            {"stock": 4, "priority": "baixa"}) is False
        any_cond = {"any": [
            {"field": "stock", "op": "lt", "value": 10},
            {"field": "overdue", "op": "eq", "value": True},
        ]}
        assert evaluator.evaluate_condition(any_cond, {"stock": 50}) is False
        assert evaluator.evaluate_condition(any_cond, {"overdue": True}) is True
        not_cond = {"not": {"field": "active", "op": "eq", "value": True}}
        assert evaluator.evaluate_condition(not_cond, {"active": False}) is True

    def test_exists_and_collections(self) -> None:
        evaluator = TriggerEvaluator()
        assert evaluator.evaluate_condition(
            {"field": "email", "op": "exists", "value": True},
            {"email": "a@b.com"}) is True
        assert evaluator.evaluate_condition(
            {"field": "email", "op": "exists", "value": True}, {}) is False
        assert evaluator.evaluate_condition(
            {"field": "tags", "op": "contains", "value": "urgente"},
            {"tags": ["normal", "urgente"]}) is True
        assert evaluator.evaluate_condition(
            {"field": "role", "op": "in", "value": ["admin", "manager"]},
            {"role": "admin"}) is True

    def test_missing_field_and_unknown_op(self) -> None:
        evaluator = TriggerEvaluator()
        assert evaluator.evaluate_condition({"field": "ghost", "op": "eq",
                                             "value": 1}, {}) is False
        assert evaluator.evaluate_condition({"field": "", "op": "eq",
                                             "value": 1}, {}) is False
        try:
            evaluator.evaluate_condition({"field": "x", "op": "~",
                                          "value": 1}, {"x": 1})
            assert False, "expected ValueError"
        except ValueError:
            pass


class TestTriggerCondition:
    def test_implements_core_trigger_interface(self) -> None:
        definition = TriggerDefinition(
            "t-low", "Estoque baixo", "condition",
            condition={"field": "stock", "op": "lt", "value": 10})
        condition = TriggerCondition(definition)
        assert condition.evaluate({"data": {"stock": 4}}) is True
        assert condition.evaluate({"data": {"stock": 15}}) is False

    def test_predicate_based(self) -> None:
        definition = TriggerDefinition(
            "t-pred", "Predicado", "condition",
            predicate=lambda d: d.get("sku") == "sku-1")
        assert TriggerCondition(definition).evaluate({"sku": "sku-1"}) is True
        assert TriggerCondition(definition).evaluate({"sku": "sku-2"}) is False


class TestTriggerRegistry:
    def test_crud(self) -> None:
        registry = TriggerRegistry()
        registry.register(TriggerDefinition("t1", "Um", "event"))
        assert registry.get("t1").name == "Um"
        assert registry.list() == ["t1"]
        assert registry.set_enabled("t1", False) is True
        assert registry.get("t1").enabled is False
        assert registry.set_enabled("ghost", False) is False
        assert registry.remove("t1") is True
        assert registry.remove("t1") is False
        assert registry.snapshot() == {"triggers": 0}


class TestTriggerRouter:
    def test_route_condition_and_event(self) -> None:
        registry = TriggerRegistry()
        history = TriggerHistory()
        events = AutomationEvents()
        fired: list[str] = []
        events.on(AutomationEventType.TRIGGER_FIRED,
                  lambda d: fired.append(d["trigger_id"]))
        router = TriggerRouter(registry, history=history, events=events)
        registry.register(TriggerDefinition(
            "t-low", "Estoque baixo", "condition",
            condition={"field": "stock", "op": "lt", "value": 10}))
        registry.register(TriggerDefinition(
            "t-pedido", "Novo pedido", "event",
            config={"event_type": "order.created"}))

        assert router.route(TriggerEvent("stock.updated", {"stock": 4})) == ["t-low"]
        assert router.route(TriggerEvent("stock.updated", {"stock": 20})) == []
        assert router.route(TriggerEvent("order.created")) == ["t-pedido"]
        assert router.route(TriggerEvent("order.cancelled")) == []
        assert fired == ["t-low", "t-pedido"]
        assert history.count() == 2
        assert history.count("t-low") == 1

    def test_disabled_trigger_ignored(self) -> None:
        registry = TriggerRegistry()
        router = TriggerRouter(registry)
        definition = TriggerDefinition(
            "t-off", "Off", "condition",
            condition={"field": "x", "op": "eq", "value": 1})
        registry.register(definition)
        registry.set_enabled("t-off", False)
        assert router.route(TriggerEvent("e", {"x": 1})) == []


class TestTriggerScheduler:
    def test_schedule_and_run_due(self) -> None:
        engine = TriggerEngine()
        fired: list[str] = []
        engine.router.history = None  # not needed here
        # wrap router to observe
        engine.register_time("t-check", "Checagem", 60,
                             predicate=lambda d: True)
        # simulate 90s elapsed
        fired_now = engine.run_due(now=1000.0)
        assert fired_now == ["t-check"]
        assert engine.scheduler.due(1050.0) == []
        assert engine.scheduler.due(1061.0) == ["t-check"]

    def test_unschedule(self) -> None:
        engine = TriggerEngine()
        engine.register_time("t-a", "A", 10)
        assert engine.scheduler.unschedule("t-a") is True
        assert engine.scheduler.unschedule("t-a") is False


class TestTriggerEngine:
    def test_register_and_fire(self) -> None:
        metrics = AutomationMetrics()
        engine = TriggerEngine(metrics=metrics)
        engine.register_condition("t-low", "Estoque baixo",
                                  {"field": "stock", "op": "lt", "value": 10})
        engine.register_event("t-pedido", "Pedido", "order.created")

        assert engine.fire("stock.updated", {"stock": 3}) == ["t-low"]
        assert engine.fire("stock.updated", {"stock": 12}) == []
        assert engine.fire("order.created") == ["t-pedido"]
        assert engine.list() == ["t-low", "t-pedido"]
        assert engine.firing_history() != []
        assert metrics.counter("triggers.fired") == 2

    def test_evaluate_direct(self) -> None:
        engine = TriggerEngine()
        engine.register_condition("t-low", "Baixo",
                                  {"field": "stock", "op": "lt", "value": 10})
        assert engine.evaluate("t-low", {"stock": 4}) is True
        assert engine.evaluate("t-low", {"stock": 20}) is False
        assert engine.evaluate("ghost") is False

    def test_disable_and_remove(self) -> None:
        engine = TriggerEngine()
        engine.register_condition("t-x", "X", {"field": "a", "op": "eq",
                                               "value": 1})
        assert engine.disable("t-x") is True
        assert engine.fire("e", {"a": 1}) == []
        assert engine.enable("t-x") is True
        assert engine.fire("e", {"a": 1}) == ["t-x"]
        assert engine.remove("t-x") is True

    def test_time_trigger_with_metrics(self) -> None:
        engine = TriggerEngine()
        engine.register_time("t-diario", "Verificação diária", 86400)
        assert engine.run_due(now=86400.0) == ["t-diario"]
        assert engine.run_due(now=86400.0) == []  # not due again immediately
        assert engine.run_due(now=172800.0) == ["t-diario"]

    def test_user_example_low_stock(self) -> None:
        """Sistema verifica estoque -> se menor que limite, aciona reposição."""
        engine = TriggerEngine()
        engine.register_condition(
            "t-reposicao", "Reposição de estoque",
            {"all": [
                {"field": "stock", "op": "lt", "value": 10},
                {"field": "store.open", "op": "eq", "value": True},
            ]})
        assert engine.fire("stock.updated",
                           {"stock": 5, "store": {"open": True}}) == ["t-reposicao"]
        assert engine.fire("stock.updated",
                           {"stock": 5, "store": {"open": False}}) == []
        assert engine.fire("stock.updated",
                           {"stock": 25, "store": {"open": True}}) == []
