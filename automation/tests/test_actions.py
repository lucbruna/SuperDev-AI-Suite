"""Tests for the actions subsystem (Volume 20, Fase 4)."""

from __future__ import annotations

import time
from typing import Any

import pytest

from automation.actions.action_builder import ActionBuilder
from automation.actions.action_engine import ActionEngine
from automation.actions.action_models import ActionDefinition, ActionResult
from automation.actions.action_policy import ActionPolicy
from automation.actions.action_registry import ActionRegistry
from automation.actions.action_router import ActionRouter
from automation.actions.action_runner import ActionRunner
from automation.actions.action_validator import ActionValidator
from automation.automation_events import AutomationEventType, AutomationEvents
from automation.automation_metrics import AutomationMetrics


class TestActionBuilder:
    def test_build(self) -> None:
        builder = (ActionBuilder()
                   .id("email.send")
                   .name("Enviar email")
                   .description("Envia um email transacional")
                   .required_params("to", "subject")
                   .timeout(5.0)
                   .retries(2, delay=0.05)
                   .handler(lambda p: {"sent": True}))
        definition, handler = builder.build()
        assert definition.action_id == "email.send"
        assert definition.required_params == ["to", "subject"]
        assert definition.retries == 2
        assert definition.timeout == 5.0
        assert handler({"to": "a"}) == {"sent": True}


class TestActionValidator:
    def test_validate_definition(self) -> None:
        validator = ActionValidator()
        assert validator.validate_definition(ActionDefinition("a", "A")) == []
        issues = validator.validate_definition(ActionDefinition("", "A"))
        assert "action_id is required" in issues
        issues = validator.validate_definition(
            ActionDefinition("a", "", retries=-1, timeout=-2))
        assert "name is required" in issues
        assert any("retries" in i for i in issues)
        assert any("timeout" in i for i in issues)

    def test_validate_params(self) -> None:
        validator = ActionValidator()
        definition = ActionDefinition("email.send", "Email",
                                      required_params=["to", "subject"])
        assert validator.validate_params(definition, {"to": "a",
                                                     "subject": "s"}) == []
        issues = validator.validate_params(definition, {"to": "a"})
        assert issues == ["missing required param: subject"]

    def test_coerce_params(self) -> None:
        validator = ActionValidator()
        definition = ActionDefinition(
            "order.create", "Pedido",
            params_schema={"quantity": "int", "price": "float",
                           "active": "bool"})
        params = validator.coerce_params(definition, {
            "quantity": "3", "price": "9.9", "active": "true", "other": "x"})
        assert params["quantity"] == 3
        assert params["price"] == 9.9
        assert params["active"] is True
        assert params["other"] == "x"


class TestActionRegistry:
    def test_crud(self) -> None:
        registry = ActionRegistry()
        registry.register(ActionDefinition("a1", "Um"), lambda p: {})
        assert registry.has("a1") is True
        assert registry.get_handler("a1") is not None
        assert registry.list() == ["a1"]
        assert registry.snapshot() == {"actions": 1}
        assert registry.remove("a1") is True
        assert registry.remove("a1") is False
        assert registry.has("a1") is False


class TestActionRunner:
    def test_implements_core_interface(self) -> None:
        registry = ActionRegistry()
        registry.register(ActionDefinition("ping", "Ping"), lambda p: {"pong": True})
        runner = ActionRunner(registry)
        assert runner.execute("ping", {}) == {"pong": True}
        with pytest.raises(KeyError):
            runner.execute("ghost", {})

    def test_run_success(self) -> None:
        registry = ActionRegistry()
        registry.register(ActionDefinition("ping", "Ping"), lambda p: {"pong": True})
        result = ActionRunner(registry).run(registry.get_definition("ping"), {})
        assert result.success is True
        assert result.attempts == 1

    def test_run_retries_then_succeeds(self) -> None:
        registry = ActionRegistry()
        attempts = [0]

        def flaky(_: dict[str, Any]) -> dict[str, bool]:
            attempts[0] += 1
            if attempts[0] == 1:
                raise ConnectionError("timeout de rede")
            return {"ok": True}

        definition = ActionDefinition("http.get", "GET", retries=2,
                                      retry_delay=0.01)
        registry.register(definition, flaky)
        result = ActionRunner(registry).run(definition, {})
        assert result.success is True
        assert result.attempts == 2

    def test_run_fails_after_retries(self) -> None:
        registry = ActionRegistry()
        definition = ActionDefinition("http.get", "GET", retries=1,
                                      retry_delay=0.01)

        def always_fail(_: dict[str, Any]) -> None:
            raise RuntimeError("falha persistente")

        registry.register(definition, always_fail)
        result = ActionRunner(registry).run(definition, {})
        assert result.success is False
        assert result.attempts == 2
        assert "falha persistente" in (result.error or "")

    def test_run_timeout(self) -> None:
        registry = ActionRegistry()

        def slow(_: dict[str, Any]) -> dict[str, bool]:
            time.sleep(0.05)
            return {"done": True}

        definition = ActionDefinition("slow.action", "Lento", timeout=0.01)
        registry.register(definition, slow)
        result = ActionRunner(registry).run(definition, {})
        assert result.success is False
        assert "timeout" in (result.error or "")


class TestActionPolicy:
    def test_rate_limit(self) -> None:
        policy = ActionPolicy(max_calls_per_window=2, window_seconds=60.0)
        assert policy.reason("api.call") is None
        policy.record_call("api.call", now=1.0)
        policy.record_call("api.call", now=2.0)
        assert "rate limit" in (policy.reason("api.call", now=3.0))
        assert policy.remaining("api.call", now=3.0) == 0
        # after the window, allowed again
        assert policy.reason("api.call", now=70.0) is None

    def test_allow_and_deny(self) -> None:
        policy = ActionPolicy()
        policy.deny("drop.database")
        assert "denied" in policy.reason("drop.database")
        policy.set_allowlist(["email.send", "api.call"])
        assert policy.reason("agent.run") is not None
        assert policy.reason("email.send") is None

    def test_cooldown(self) -> None:
        policy = ActionPolicy(cooldown_seconds=10.0)
        policy.record_call("order.create", now=100.0)
        assert "cooldown" in policy.reason("order.create", now=105.0)
        assert policy.reason("order.create", now=115.0) is None


class TestActionRouter:
    def test_prefix_routing(self) -> None:
        registry = ActionRegistry()
        router = ActionRouter(registry)
        seen: list[str] = []
        router.register_prefix("email.", lambda action_id, p: seen.append(action_id))
        assert router.can_route("email.send") is True
        router.route("email.send", {"to": "a"})
        assert seen == ["email.send"]

    def test_registry_fallback_and_unknown(self) -> None:
        registry = ActionRegistry()
        registry.register(ActionDefinition("ping", "Ping"), lambda p: {"ok": 1})
        router = ActionRouter(registry)
        assert router.route("ping", {}) == {"ok": 1}
        assert router.can_route("ghost") is False
        with pytest.raises(KeyError):
            router.route("ghost", {})


class TestActionEngine:
    def _build(self) -> ActionEngine:
        return ActionEngine()

    def test_register_and_execute(self) -> None:
        engine = self._build()
        definition, handler = (engine.build()
                               .id("stock.check")
                               .name("Verificar estoque")
                               .required_params("sku")
                               .handler(lambda p: {"in_stock": True})
                               .build())
        assert engine.register(definition, handler) is None
        result = engine.execute("stock.check", {"sku": "sku-1"})
        assert result.success is True
        assert result.result == {"in_stock": True}
        assert len(engine.history()) == 1
        assert engine.has("stock.check") is True

    def test_unknown_action_with_fallback(self) -> None:
        engine = self._build()
        result = engine.execute("legacy.call", {"x": 1},
                                fallback=lambda a, p: {"routed": a})
        assert result.success is True
        assert result.result == {"routed": "legacy.call"}
        result = engine.execute("ghost.action")
        assert result.success is False
        assert "unknown action" in (result.error or "")

    def test_required_param_missing(self) -> None:
        engine = self._build()
        definition, handler = (engine.build()
                               .id("email.send").name("Email")
                               .required_params("to")
                               .handler(lambda p: {"sent": True})
                               .build())
        engine.register(definition, handler)
        result = engine.execute("email.send", {"subject": "oi"})
        assert result.success is False
        assert "missing required param: to" in (result.error or "")

    def test_policy_blocks(self) -> None:
        policy = ActionPolicy(max_calls_per_window=1, window_seconds=60.0)
        engine = ActionEngine(policy=policy)
        definition, handler = (engine.build()
                               .id("api.call").name("Chamada API")
                               .handler(lambda p: {"ok": True})
                               .build())
        engine.register(definition, handler)
        assert engine.execute("api.call").success is True
        blocked = engine.execute("api.call")
        assert blocked.success is False
        assert "policy blocked" in (blocked.error or "")

    def test_disabled_action(self) -> None:
        engine = self._build()
        definition, handler = (engine.build()
                               .id("maintenance").name("Manutenção")
                               .enabled(False)
                               .handler(lambda p: {})
                               .build())
        engine.register(definition, handler)
        result = engine.execute("maintenance")
        assert result.success is False
        assert "disabled" in (result.error or "")

    def test_schema_coercion_on_execute(self) -> None:
        engine = self._build()
        received: dict[str, Any] = {}
        definition, handler = (engine.build()
                               .id("order.create").name("Criar pedido")
                               .required_params("quantity")
                               .params_schema({"quantity": "int"})
                               .handler(lambda p: received.update(p) or {"ok": True})
                               .build())
        engine.register(definition, handler)
        result = engine.execute("order.create", {"quantity": "5"})
        assert result.success is True
        assert received["quantity"] == 5

    def test_events_and_metrics(self) -> None:
        events = AutomationEvents()
        metrics = AutomationMetrics()
        engine = ActionEngine(events=events, metrics=metrics)
        completed: list[str] = []
        events.on(AutomationEventType.TASK_COMPLETED,
                  lambda d: completed.append(d["action_id"]))
        definition, handler = (engine.build()
                               .id("ping").name("Ping")
                               .handler(lambda p: {"pong": True})
                               .build())
        engine.register(definition, handler)
        engine.execute("ping")
        assert completed == ["ping"]
        assert metrics.counter("actions.completed") == 1

    def test_user_example_erp_actions(self) -> None:
        """Ações do fluxo de reposição: stock.check -> order.create -> erp.update."""
        engine = self._build()
        engine.register(*engine.build().id("stock.check").name("Checar estoque")
                        .handler(lambda p: {"available": p.get("qty", 0) >= p.get("min", 10)})
                        .build())
        engine.register(*engine.build().id("order.create").name("Criar pedido")
                        .required_params("supplier")
                        .handler(lambda p: {"order_id": "PO-2026-001",
                                            "supplier": p["supplier"]})
                        .build())
        engine.register(*engine.build().id("erp.update").name("Atualizar ERP")
                        .handler(lambda p: {"synced": True})
                        .build())
        engine.register(*engine.build().id("email.send").name("Notificar")
                        .required_params("to")
                        .handler(lambda p: {"sent": True})
                        .build())

        stock = engine.execute("stock.check", {"qty": 5, "min": 10})
        assert stock.success is True
        assert stock.result["available"] is False
        order = engine.execute("order.create", {"supplier": "Fornecedor A"})
        assert order.result["order_id"] == "PO-2026-001"
        assert engine.execute("erp.update").result["synced"] is True
        assert engine.execute("email.send", {"to": "compras@loja.com"}).success is True
