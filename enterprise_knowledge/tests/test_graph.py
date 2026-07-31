"""Tests for the graph/ subsystem (Volume 27, Fase 2)."""

from __future__ import annotations

import pytest

from enterprise_knowledge.graph.entity_extractor import EntityExtractor
from enterprise_knowledge.graph.graph_engine import GraphEngine
from enterprise_knowledge.graph.graph_query import GraphQuery
from enterprise_knowledge.graph.graph_visualizer import GraphVisualizer
from enterprise_knowledge.graph.node_manager import NodeManager
from enterprise_knowledge.graph.relationship_manager import RelationshipManager
from enterprise_knowledge.knowledge_factory import build_engine
from enterprise_knowledge.knowledge_models import NodeType, RelationshipType
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry


@pytest.fixture
def engine():
    engine = build_engine()
    engine.attach_subsystem(
        "graph_engine",
        GraphEngine(events=engine.events, metrics=engine.metrics,
                    config=engine.config, security=engine.security,
                    registry=engine.registry))
    return engine


def _chain(engine):
    """Builds: Cliente João -> Projeto ERP -> Banco PostgreSQL
    -> Problema de performance -> Índice SQL."""
    cliente = engine.graph_engine.add_node("Cliente João", NodeType.PERSON)
    projeto = engine.graph_engine.add_node("Projeto ERP", NodeType.PROJECT)
    banco = engine.graph_engine.add_node("Banco PostgreSQL",
                                         NodeType.DATABASE)
    problema = engine.graph_engine.add_node("Problema de performance",
                                            NodeType.PROBLEM)
    solucao = engine.graph_engine.add_node("Índice SQL", NodeType.SOLUTION)
    engine.graph_engine.connect(cliente.node_id, projeto.node_id,
                                RelationshipType.BELONGS_TO)
    engine.graph_engine.connect(projeto.node_id, banco.node_id,
                                RelationshipType.USES)
    engine.graph_engine.connect(banco.node_id, problema.node_id,
                                RelationshipType.HAS)
    engine.graph_engine.connect(problema.node_id, solucao.node_id,
                                RelationshipType.RESOLVED_BY)
    return cliente, projeto, banco, problema, solucao


class TestNodeManager:
    def test_crud(self):
        registry = EnterpriseKnowledgeRegistry()
        manager = NodeManager(registry=registry)
        node = manager.create("ERP", NodeType.PROJECT, {"módulos": 12})
        assert node.node_id.startswith("node-")
        assert manager.get(node.node_id) is node
        assert manager.list() == [node.node_id]
        manager.update(node.node_id, label="ERP v2")
        assert manager.get(node.node_id).label == "ERP v2"
        assert manager.remove(node.node_id) is True

    def test_find_by_label_and_type(self, engine):
        engine.graph_engine.add_node("PostgreSQL", NodeType.DATABASE)
        engine.graph_engine.add_node("MySQL", NodeType.DATABASE)
        engine.graph_engine.add_node("ERP", NodeType.PROJECT)
        assert len(engine.graph_engine.find_type(NodeType.DATABASE)) == 2
        assert len(engine.graph_engine.find("ERP")) == 1


class TestRelationshipManager:
    def test_requires_both_nodes(self):
        registry = EnterpriseKnowledgeRegistry()
        manager = RelationshipManager(registry=registry)
        assert manager.create("a", "b") is None

    def test_neighbors_and_between(self, engine):
        cliente, projeto, banco, _, _ = _chain(engine)
        neighbors = engine.graph_engine.neighbors(projeto.node_id)
        labels = {n["node_id"] for n in neighbors}
        assert cliente.node_id in labels and banco.node_id in labels
        assert engine.graph_engine.connected(projeto.node_id, banco.node_id)
        assert not engine.graph_engine.connected(banco.node_id, projeto.node_id)


class TestGraphQuery:
    def test_shortest_path(self, engine):
        cliente, _, _, problema, solucao = _chain(engine)
        path = engine.graph_engine.path(cliente.node_id, solucao.node_id)
        assert path[0] == cliente.node_id
        assert path[-1] == solucao.node_id
        assert len(path) == 5

    def test_path_exists_and_unreachable(self, engine):
        cliente, _, _, _, solucao = _chain(engine)
        assert engine.graph_engine.query.path_exists(cliente.node_id,
                                                    solucao.node_id)
        isolated = engine.graph_engine.add_node("isolado", NodeType.CONCEPT)
        assert engine.graph_engine.query.path_exists(
            cliente.node_id, isolated.node_id) is False

    def test_reachable_and_components(self, engine):
        cliente, _, _, _, _ = _chain(engine)
        isolated = engine.graph_engine.add_node("solo", NodeType.CONCEPT)
        reachable = engine.graph_engine.reachable_from(cliente.node_id)
        assert isolated.node_id not in reachable
        assert len(reachable) == 4
        components = engine.graph_engine.components()
        assert len(components) == 2

    def test_most_connected(self, engine):
        _chain(engine)
        ranked = engine.graph_engine.most_connected(limit=2)
        assert ranked[0][0]  # some node id
        assert ranked[0][1] >= 2  # projeto has degree 2


class TestEntityExtractor:
    def test_entities(self):
        extractor = EntityExtractor()
        found = extractor.entities("O projeto ERP usa PostgreSQL")
        names = {e["name"] for e in found}
        assert "projeto" in names
        assert "ERP" in names

    def test_agent_mentions(self):
        extractor = EntityExtractor()
        found = extractor.entities("o agente @planner sugeriu")
        assert any(e["name"] == "planner"
                   and e["node_type"] == "agent" for e in found)

    def test_relations(self):
        extractor = EntityExtractor()
        found = extractor.relations("banco possui problema")
        assert found and found[0]["rel_type"] == "has"
        assert found[0]["source"] == "banco"
        assert found[0]["target"] == "problema"


class TestGraphVisualizer:
    def test_ascii_tree(self, engine):
        _, projeto, _, _, _ = _chain(engine)
        tree = engine.graph_engine.ascii(projeto.node_id, max_depth=2)
        assert "Projeto ERP" in tree
        assert "Cliente João" in tree

    def test_mermaid(self, engine):
        _chain(engine)
        mermaid = engine.graph_engine.mermaid()
        assert mermaid.startswith("graph TD")
        assert "resolved_by" in mermaid


class TestGraphEngine:
    def test_events_and_metrics(self, engine):
        received = []
        engine.events.on("__never__", received.append)  # noqa: B021
        node = engine.graph_engine.add_node("Decisão", NodeType.DECISION)
        assert engine.graph_engine.get_node(node.node_id) is node
        assert engine.metrics.snapshot()["counters"]["ek.nodes"] >= 1

    def test_extraction_wiring(self, engine):
        entities = engine.graph_engine.extract_entities(
            "O projeto usa PostgreSQL")
        relations = engine.graph_engine.extract_relations(
            "projeto usa PostgreSQL")
        assert entities
        assert relations

    def test_stats(self, engine):
        _chain(engine)
        stats = engine.graph_engine.stats()
        assert stats["nodes"] >= 5
        assert stats["relationships"] >= 4
        assert stats["components"] == 1
