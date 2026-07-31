"""Tests for the decisions subsystem (Volume 20, Fase 5)."""

from __future__ import annotations

from automation.decisions.decision_builder import DecisionBuilder
from automation.decisions.decision_engine import DecisionEngine
from automation.decisions.decision_models import DecisionResult
from automation.decisions.decision_validator import DecisionValidator


class TestDecisionBuilder:
    def test_build_tree(self) -> None:
        tree = (DecisionBuilder()
                .id("t-estoque")
                .name("Decisão de reposição")
                .node("raiz", "Estoque abaixo do limite?")
                .branch("raiz", "baixo",
                        {"field": "stock", "op": "lt", "value": 10},
                        to="repor")
                .branch("raiz", "ok",
                        {"field": "stock", "op": "gte", "value": 10},
                        to="manter")
                .leaf("repor", "order.create", {"supplier": "default"})
                .leaf("manter", "noop")
                .root("raiz")
                .build())
        assert tree.tree_id == "t-estoque"
        assert tree.root_id == "raiz"
        assert len(tree.nodes) == 3
        assert tree.nodes["repor"].action == "order.create"


class TestDecisionTree:
    def _tree(self):
        return (DecisionBuilder()
                .id("t-estoque").name("Reposição")
                .node("raiz", "Estoque abaixo do limite?")
                .branch("raiz", "baixo",
                        {"field": "stock", "op": "lt", "value": 10},
                        to="repor")
                .leaf("repor", "order.create", {"supplier": "Fornecedor A"})
                .leaf("manter", "noop")
                .root("raiz")
                .build())

    def test_decide_triggers_action(self) -> None:
        tree = self._tree()
        result = tree.decide({"stock": 4})
        assert result.action == "order.create"
        assert result.params["supplier"] == "Fornecedor A"
        assert result.path == ["raiz", "repor"]
        assert result.decision == "order.create"

    def test_decide_no_branch_matched(self) -> None:
        tree = self._tree()
        result = tree.decide({"stock": 20})
        assert result.decision == "no_branch_matched"
        assert result.action is None

    def test_nested_path_condition(self) -> None:
        tree = (DecisionBuilder()
                .id("t-nested").name("Aninhado")
                .node("raiz")
                .branch("raiz", "b", {"field": "store.stock.sku-1",
                                      "op": "lt", "value": 5},
                        to="pedido")
                .leaf("pedido", "order.create")
                .root("raiz")
                .build())
        result = tree.decide({"store": {"stock": {"sku-1": 2}}})
        assert result.action == "order.create"
        result = tree.decide({"store": {"stock": {"sku-1": 20}}})
        assert result.decision == "no_branch_matched"


class TestDecisionValidator:
    def _valid(self):
        return (DecisionBuilder()
                .id("t-1").name("Válida")
                .node("raiz")
                .branch("raiz", "b", {"field": "x", "op": "eq",
                                      "value": 1}, to="folha")
                .leaf("folha", "noop")
                .build())

    def test_valid_tree(self) -> None:
        assert DecisionValidator().validate(self._valid()) == []

    def test_missing_root(self) -> None:
        tree = self._valid()
        tree.root_id = "ghost"
        issues = DecisionValidator().validate(tree)
        assert any("root" in i for i in issues)

    def test_dangling_branch_target(self) -> None:
        tree = (DecisionBuilder()
                .id("t-2").name("Quebrada")
                .node("raiz")
                .branch("raiz", "b", {"field": "x", "op": "eq",
                                      "value": 1}, to="ghost")
                .build())
        issues = DecisionValidator().validate(tree)
        assert any("unknown node" in i for i in issues)

    def test_no_nodes(self) -> None:
        tree = (DecisionBuilder().id("t-3").name("Vazia").build())
        assert "tree has no nodes" in DecisionValidator().validate(tree)


class TestDecisionEngine:
    def test_register_and_decide(self) -> None:
        engine = DecisionEngine()
        tree = (engine.build()
                .id("t-pedido").name("Pedido")
                .node("raiz", "Pagamento aprovado?")
                .branch("raiz", "aprovado",
                        {"field": "payment", "op": "eq", "value": "approved"},
                        to="processar")
                .leaf("processar", "ship.order")
                .leaf("recusar", "cancel.order")
                .root("raiz")
                .build())
        assert engine.register(tree) is None
        result = engine.decide("t-pedido", {"payment": "approved"})
        assert result is not None
        assert result.action == "ship.order"
        assert engine.decide("t-pedido", {"payment": "declined"}).decision \
            == "no_branch_matched"
        assert engine.list() == ["t-pedido"]
        assert len(engine.decision_history()) == 2

    def test_unknown_tree(self) -> None:
        engine = DecisionEngine()
        assert engine.decide("ghost", {}) is None

    def test_invalid_tree_rejected(self) -> None:
        engine = DecisionEngine()
        tree = (engine.build()
                .id("t-bad").name("Ruim")
                .node("raiz")
                .branch("raiz", "b", {"field": "x", "op": "eq",
                                      "value": 1}, to="ghost")
                .build())
        issues = engine.register(tree)
        assert issues is not None
        assert "unknown node" in issues[0]

    def test_remove(self) -> None:
        engine = DecisionEngine()
        tree = (engine.build()
                .id("t-rm").name("Remover")
                .leaf("folha", "noop")
                .build())
        engine.register(tree)
        assert engine.remove("t-rm") is True
        assert engine.remove("t-rm") is False

    def test_user_example_stock_decision(self) -> None:
        """Árvore de decisão: estoque menor que limite? -> repor / manter."""
        engine = DecisionEngine()
        tree = (engine.build()
                .id("t-reposicao").name("Reposição inteligente")
                .node("raiz", "Estoque menor que o limite?")
                .branch("raiz", "sim",
                        {"all": [
                            {"field": "stock", "op": "lt", "value": 10},
                            {"field": "store.open", "op": "eq", "value": True},
                        ]},
                        to="repor")
                .leaf("repor", "order.create",
                      {"supplier": "Fornecedor A", "qty": 50})
                .leaf("manter", "noop")
                .root("raiz")
                .build())
        engine.register(tree)
        result = engine.decide("t-reposicao", {"stock": 3, "store": {"open": True}})
        assert result.action == "order.create"
        assert result.params == {"supplier": "Fornecedor A", "qty": 50}
        # loja fechada -> nenhuma branch
        assert engine.decide("t-reposicao",
                             {"stock": 3, "store": {"open": False}}).decision \
            == "no_branch_matched"
        # estoque ok
        assert engine.decide("t-reposicao",
                             {"stock": 25, "store": {"open": True}}).decision \
            == "no_branch_matched"
