import pytest
from workflow_engine.graph.graph import WorkflowGraph
from workflow_engine.graph.node import WorkflowNode, NodeType
from workflow_engine.graph.edge import WorkflowEdge
from workflow_engine.state.state_machine import WorkflowStateMachine, WorkflowState
from workflow_engine.retry.retry_policy import RetryPolicy


class TestWorkflowGraph:
    def test_criar_grafo(self):
        graph = WorkflowGraph()
        assert graph is not None

    def test_adicionar_no(self):
        graph = WorkflowGraph()
        node = WorkflowNode(id="node1", type=NodeType.SHELL, name="node1", config={"command": "echo ok"})
        graph.add_node(node)
        assert graph.get_node("node1") is not None
        assert graph.get_node("node1").id == "node1"

    def test_adicionar_aresta(self):
        graph = WorkflowGraph()
        n1 = WorkflowNode(id="node1", type=NodeType.SHELL, name="node1")
        n2 = WorkflowNode(id="node2", type=NodeType.SHELL, name="node2")
        graph.add_node(n1)
        graph.add_node(n2)
        edge = WorkflowEdge(id="e1", source_node_id="node1", target_node_id="node2")
        graph.add_edge(edge)
        assert graph.get_node("node1") is not None
        assert graph.get_node("node2") is not None

    def test_ordenacao_topologica(self):
        graph = WorkflowGraph()
        a = WorkflowNode(id="a", type=NodeType.SHELL, name="a")
        b = WorkflowNode(id="b", type=NodeType.SHELL, name="b")
        c = WorkflowNode(id="c", type=NodeType.SHELL, name="c")
        graph.add_node(a)
        graph.add_node(b)
        graph.add_node(c)
        graph.add_edge(WorkflowEdge(id="e1", source_node_id="a", target_node_id="b"))
        graph.add_edge(WorkflowEdge(id="e2", source_node_id="b", target_node_id="c"))

        order = graph.topological_sort()
        ids = [n.id for n in order]
        assert ids.index("a") < ids.index("b")
        assert ids.index("b") < ids.index("c")

    def test_deteccao_ciclo(self):
        graph = WorkflowGraph()
        a = WorkflowNode(id="a", type=NodeType.SHELL, name="a")
        b = WorkflowNode(id="b", type=NodeType.SHELL, name="b")
        graph.add_node(a)
        graph.add_node(b)
        graph.add_edge(WorkflowEdge(id="e1", source_node_id="a", target_node_id="b"))
        graph.add_edge(WorkflowEdge(id="e2", source_node_id="b", target_node_id="a"))

        errors = graph.validate()
        assert any("cycle" in e.lower() for e in errors)

    def test_sem_ciclo(self):
        graph = WorkflowGraph()
        a = WorkflowNode(id="a", type=NodeType.SHELL, name="a")
        b = WorkflowNode(id="b", type=NodeType.SHELL, name="b")
        graph.add_node(a)
        graph.add_node(b)
        graph.add_edge(WorkflowEdge(id="e1", source_node_id="a", target_node_id="b"))

        errors = graph.validate()
        assert len(errors) == 0


class TestStateMachine:
    def test_estados(self):
        sm = WorkflowStateMachine()
        assert sm.can_transition(WorkflowState.CREATED, WorkflowState.READY)

    def test_transicoes(self):
        sm = WorkflowStateMachine()
        rec = sm.transition("wf1", WorkflowState.CREATED, WorkflowState.READY)
        assert rec.from_state == WorkflowState.CREATED
        assert rec.to_state == WorkflowState.READY

    def test_transicao_invalida(self):
        sm = WorkflowStateMachine()
        with pytest.raises(ValueError):
            sm.transition("wf1", WorkflowState.CREATED, WorkflowState.COMPLETED)


class TestRetryPolicy:
    def test_politica_padrao(self):
        policy = RetryPolicy()
        assert policy.max_retries == 3
        assert policy.delay == 1.0

    def test_calculo_delay(self):
        policy = RetryPolicy(delay=1.0, backoff_factor=2.0)
        assert policy.get_delay(0) == 0.0
        assert policy.get_delay(1) == pytest.approx(2.0, rel=0.5)
        assert policy.get_delay(2) == pytest.approx(4.0, rel=0.5)

    def test_deve_tentar(self):
        policy = RetryPolicy(max_retries=3)
        assert policy.should_retry(0) is True
        assert policy.should_retry(2) is True
        assert policy.should_retry(3) is False
