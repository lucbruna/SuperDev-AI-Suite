"""Testes unitários para o ConditionNode com parser seguro."""

import pytest
from workflow_engine.nodes.condition_node import (
    ConditionNode,
    safe_condition_eval,
    _safe_eval_node,
)


class TestSafeConditionEval:
    """Testes para a função safe_condition_eval."""

    def test_comparacao_igualdade(self):
        assert safe_condition_eval("x == 5", {"x": 5}) is True
        assert safe_condition_eval("x == 5", {"x": 3}) is False

    def test_comparacao_desigualdade(self):
        assert safe_condition_eval("x != 5", {"x": 3}) is True
        assert safe_condition_eval("x != 5", {"x": 5}) is False

    def test_comparacao_maior(self):
        assert safe_condition_eval("x > 5", {"x": 10}) is True
        assert safe_condition_eval("x > 5", {"x": 3}) is False

    def test_comparacao_menor(self):
        assert safe_condition_eval("x < 5", {"x": 3}) is True
        assert safe_condition_eval("x < 5", {"x": 10}) is False

    def test_operadores_booleanos(self):
        assert safe_condition_eval("a and b", {"a": True, "b": True}) is True
        assert safe_condition_eval("a and b", {"a": True, "b": False}) is False
        assert safe_condition_eval("a or b", {"a": False, "b": True}) is True
        assert safe_condition_eval("not a", {"a": True}) is False

    def test_operadores_aritmeticos(self):
        assert safe_condition_eval("x + 1 == 6", {"x": 5}) is True
        assert safe_condition_eval("x * 2 == 10", {"x": 5}) is True
        assert safe_condition_eval("x // 2 == 2", {"x": 5}) is True
        assert safe_condition_eval("x % 2 == 1", {"x": 5}) is True

    def test_constantes_booleanas(self):
        assert safe_condition_eval("True", {}) is True
        assert safe_condition_eval("False", {}) is False
        assert safe_condition_eval("None is None", {}) is True

    def test_operador_in(self):
        assert safe_condition_eval("x in lista", {"x": 1, "lista": [1, 2, 3]}) is True
        assert safe_condition_eval("x in lista", {"x": 5, "lista": [1, 2, 3]}) is False

    def test_expressao_composta(self):
        context = {"idade": 25, "ativo": True}
        assert safe_condition_eval("idade >= 18 and ativo", context) is True
        assert safe_condition_eval("idade < 18 or not ativo", context) is False

    def test_bloqueio_chamadas_funcao(self):
        with pytest.raises(ValueError, match="Function calls are not allowed"):
            safe_condition_eval("__import__('os')", {})

    def test_bloqueio_exec(self):
        with pytest.raises(ValueError, match="not allowed"):
            safe_condition_eval("exec('import os')", {})

    def test_bloqueio_eval(self):
        with pytest.raises(ValueError, match="not allowed"):
            safe_condition_eval("eval('1+1')", {})

    def test_bloqueio_open(self):
        with pytest.raises(ValueError, match="not allowed"):
            safe_condition_eval("open('/etc/passwd')", {})

    def test_bloqueio_getattr(self):
        with pytest.raises(ValueError, match="not allowed"):
            safe_condition_eval("getattr(obj, '__class__')", {"obj": object()})


class TestConditionNode:
    """Testes para o ConditionNode."""

    @pytest.mark.asyncio
    async def test_condicao_verdadeira(self):
        node = ConditionNode()
        node.config = {"node_id": "test-1", "expression": "x > 5"}
        result = await node.execute({"x": 10})
        assert result.status == "success"
        assert result.output["condition_result"] is True

    @pytest.mark.asyncio
    async def test_condicao_falsa(self):
        node = ConditionNode()
        node.config = {"node_id": "test-2", "expression": "x > 5"}
        result = await node.execute({"x": 3})
        assert result.status == "success"
        assert result.output["condition_result"] is False

    @pytest.mark.asyncio
    async def test_expressao_vazia(self):
        node = ConditionNode()
        node.config = {"node_id": "test-3", "expression": ""}
        result = await node.execute({})
        assert result.status == "failed"
        assert "No expression" in result.error

    @pytest.mark.asyncio
    async def test_expressao_invalida(self):
        node = ConditionNode()
        node.config = {"node_id": "test-4", "expression": "x + + +"}
        result = await node.execute({"x": 5})
        assert result.status == "failed"
        assert "evaluation error" in result.error.lower()
