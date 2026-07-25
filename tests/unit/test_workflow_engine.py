"""Testes unitários para o WorkflowEngine."""

import pytest
from workflow_engine.graph.graph import WorkflowGraph
from workflow_engine.graph.graph_builder import GraphBuilder
from workflow_engine.state.state_machine import WorkflowStateMachine
from workflow_engine.retry.retry_policy import RetryPolicy


class TestWorkflowGraph:
    """Testes para o WorkflowGraph."""

    def test_criar_grafo(self):
        graph = WorkflowGraph()
        assert graph is not None

    def test_adicionar_no(self):
        graph = WorkflowGraph()
        node = graph.add_node("node1", {"type": "shell", "command": "echo ok"})
        assert node is not None
        assert node.id == "node1"

    def test_adicionar_aresta(self):
        graph = WorkflowGraph()
        graph.add_node("node1", {"type": "shell"})
        graph.add_node("node2", {"type": "shell"})
        edge = graph.add_edge("node1", "node2")
        assert edge is not None

    def test_ordenacao_topologica(self):
        graph = WorkflowGraph()
        graph.add_node("a", {"type": "shell"})
        graph.add_node("b", {"type": "shell"})
        graph.add_node("c", {"type": "shell"})
        graph.add_edge("a", "b")
        graph.add_edge("b", "c")

        order = graph.topological_sort()
        assert order.index("a") < order.index("b")
        assert order.index("b") < order.index("c")

    def test_deteccao_ciclo(self):
        graph = WorkflowGraph()
        graph.add_node("a", {"type": "shell"})
        graph.add_node("b", {"type": "shell"})
        graph.add_edge("a", "b")
        graph.add_edge("b", "a")

        assert graph.has_cycle() is True

    def test_sem_ciclo(self):
        graph = WorkflowGraph()
        graph.add_node("a", {"type": "shell"})
        graph.add_node("b", {"type": "shell"})
        graph.add_edge("a", "b")

        assert graph.has_cycle() is False


class TestStateMachine:
    """Testes para a WorkflowStateMachine."""

    def test_estados(self):
        sm = WorkflowStateMachine()
        assert sm.current_state == "created"

    def test_transicoes(self):
        sm = WorkflowStateMachine()
        sm.transition("ready")
        assert sm.current_state == "ready"

        sm.transition("running")
        assert sm.current_state == "running"

        sm.transition("completed")
        assert sm.current_state == "completed"

    def test_transicao_invalida(self):
        sm = WorkflowStateMachine()
        with pytest.raises(ValueError):
            sm.transition("completed")  # Não pode ir de created para completed


class TestRetryPolicy:
    """Testes para o RetryPolicy."""

    def test_politica_padrao(self):
        policy = RetryPolicy()
        assert policy.max_retries == 3
        assert policy.base_delay == 1.0

    def test_calculo_delay(self):
        policy = RetryPolicy(base_delay=1.0, backoff_factor=2.0)
        assert policy.get_delay(0) == 1.0
        assert policy.get_delay(1) == 2.0
        assert policy.get_delay(2) == 4.0

    def test_deve_tentar(self):
        policy = RetryPolicy(max_retries=3)
        assert policy.should_retry(0) is True
        assert policy.should_retry(2) is True
        assert policy.should_retry(3) is False
