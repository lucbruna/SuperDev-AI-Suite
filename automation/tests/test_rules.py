"""Tests for the rules subsystem (Volume 20, Fase 5)."""

from __future__ import annotations

from automation.rules.rule_condition import RuleCondition
from automation.rules.rule_engine import RuleEngine
from automation.rules.rule_manager import RuleManager
from automation.rules.rule_models import RuleDefinition
from automation.rules.rule_prioritizer import RulePrioritizer


class TestRuleCondition:
    def test_implements_core_rule_interface(self) -> None:
        rule = RuleDefinition(
            "r-low", "Estoque baixo",
            condition={"field": "stock", "op": "lt", "value": 10})
        condition = RuleCondition(rule)
        assert condition.matches({"stock": 4}) is True
        assert condition.matches({"stock": 15}) is False
        assert condition.apply({"stock": 4}) is None  # no action set

    def test_predicate_and_action(self) -> None:
        applied: list[str] = []
        rule = RuleDefinition(
            "r-vip", "Cliente VIP",
            predicate=lambda f: f.get("tier") == "vip",
            action=lambda f: applied.append(f["customer"]) or "discount")
        condition = RuleCondition(rule)
        assert condition.matches({"tier": "vip"}) is True
        assert condition.apply({"customer": "ana"}) == "discount"
        assert applied == ["ana"]


class TestRuleManager:
    def test_crud(self) -> None:
        manager = RuleManager()
        rule = RuleDefinition("r1", "Um", priority=2)
        manager.add(rule)
        assert manager.get("r1") is rule
        assert manager.ids() == ["r1"]
        assert manager.set_enabled("r1", False) is True
        assert rule.enabled is False
        assert manager.set_enabled("ghost", False) is False
        assert manager.remove("r1") is True
        assert manager.remove("r1") is False


class TestRulePrioritizer:
    def _rules(self):
        return [RuleDefinition("low", "Baixa", priority=1),
                RuleDefinition("high", "Alta", priority=10),
                RuleDefinition("mid", "Média", priority=5)]

    def test_sort_by_priority_desc(self) -> None:
        ordered = RulePrioritizer().sort(self._rules())
        assert [r.rule_id for r in ordered] == ["high", "mid", "low"]

    def test_first_match(self) -> None:
        prioritizer = RulePrioritizer()
        rules = [
            RuleDefinition("gen", "Genérica",
                           predicate=lambda f: True, priority=1),
            RuleDefinition("esp", "Específica",
                           condition={"field": "tier", "op": "eq",
                                      "value": "vip"},
                           priority=10),
        ]
        match = prioritizer.first_match({"tier": "vip"}, rules)
        assert match is not None
        assert match.rule_id == "esp"
        assert prioritizer.first_match({"tier": "normal"}, rules).rule_id == "gen"
        assert prioritizer.first_match({}, []) is None


class TestRuleEngine:
    def test_add_and_evaluate(self) -> None:
        engine = RuleEngine()
        engine.add_rule("r-baixo", "Estoque baixo",
                        condition={"field": "stock", "op": "lt", "value": 10})
        engine.add_rule("r-vip", "Cliente VIP",
                        predicate=lambda f: f.get("tier") == "vip")
        assert engine.list() == ["r-baixo", "r-vip"]
        assert engine.evaluate({"stock": 4, "tier": "normal"}) == ["r-baixo"]
        assert engine.evaluate({"stock": 4, "tier": "vip"}) == ["r-baixo", "r-vip"]
        assert engine.evaluate({"stock": 50, "tier": "normal"}) == []

    def test_fire_applies_consequences(self) -> None:
        engine = RuleEngine()
        order: list[str] = []
        engine.add_rule(
            "r-aprovacao", "Aprovação gerente",
            condition={"field": "total", "op": "gte", "value": 500},
            action=lambda f: order.append("aprovacao") or {"approved": True},
            priority=5)
        engine.add_rule(
            "r-vip", "Desconto VIP",
            condition={"field": "tier", "op": "eq", "value": "vip"},
            action=lambda f: order.append("desconto") or {"discount": 0.1},
            priority=10)
        results = engine.fire({"total": 800, "tier": "vip"})
        # VIP has higher priority -> discount applied first
        assert [r.rule_id for r in results] == ["r-vip", "r-aprovacao"]
        assert order == ["desconto", "aprovacao"]
        assert results[0].consequence == {"discount": 0.1}
        assert results[1].consequence == {"approved": True}

    def test_fire_non_matching(self) -> None:
        engine = RuleEngine()
        engine.add_rule("r-x", "X",
                        condition={"field": "a", "op": "eq", "value": 1})
        results = engine.fire({"a": 2})
        assert len(results) == 1
        assert results[0].rule_id == "r-x"
        assert results[0].matched is False
        assert engine.rule_history() != []

    def test_disable_rule(self) -> None:
        engine = RuleEngine()
        engine.add_rule("r-off", "Off",
                        condition={"field": "a", "op": "eq", "value": 1})
        assert engine.disable("r-off") is True
        assert engine.evaluate({"a": 1}) == []
        assert engine.enable("r-off") is True
        assert engine.evaluate({"a": 1}) == ["r-off"]

    def test_history_counts(self) -> None:
        engine = RuleEngine()
        engine.add_rule("r-h", "H",
                        condition={"field": "a", "op": "eq", "value": 1})
        engine.fire({"a": 1})
        engine.fire({"a": 2})
        assert engine.history.count("r-h", matched_only=True) == 1
        assert engine.history.count("r-h") == 2

    def test_consequence_error_is_captured(self) -> None:
        engine = RuleEngine()

        def boom(_: dict[str, object]) -> None:
            raise RuntimeError("consequência falhou")

        engine.add_rule("r-boom", "Boom",
                        condition={"field": "a", "op": "eq", "value": 1},
                        action=boom)
        results = engine.fire({"a": 1})
        assert results[0].matched is True
        assert "falhou" in (results[0].error or "")

    def test_user_example_business_rules(self) -> None:
        """Regras do e-commerce: desconto VIP e aprovação para valores altos."""
        engine = RuleEngine()
        applied: list[str] = []
        engine.add_rule(
            "desconto-vip", "10% para VIP",
            condition={"field": "tier", "op": "eq", "value": "vip"},
            action=lambda f: applied.append(f"desconto para {f['customer']}"),
            priority=10)
        engine.add_rule(
            "aprovacao-gerente", "Valor alto precisa de aprovação",
            condition={"field": "total", "op": "gte", "value": 500},
            action=lambda f: applied.append("pedido enviado para o gerente"),
            priority=5)
        engine.fire({"customer": "ana", "tier": "vip", "total": 800})
        assert applied == ["desconto para ana", "pedido enviado para o gerente"]
        engine.fire({"customer": "beto", "tier": "normal", "total": 100})
        assert applied == ["desconto para ana", "pedido enviado para o gerente"]
