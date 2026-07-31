"""Tests for the knowledge graph subsystem."""

from __future__ import annotations

import pytest

from knowledge.knowledge_graph import (
    EntityExtractor,
    GraphBuilder,
    GraphMetrics,
    GraphSearch,
    GraphTraversal,
    KnowledgeGraph,
    KnowledgeGraphEngine,
    RelationExtractor,
)
from knowledge.knowledge_models import Entity, Relation


class TestKnowledgeGraph:
    def test_add_entities_and_relations(self) -> None:
        graph = KnowledgeGraph()
        graph.add_entity(Entity(name="SuperDev", entity_type="project"))
        graph.add_entity(Entity(name="Python", entity_type="language"))
        graph.add_relation(Relation(source="SuperDev", target="Python", relation_type="uses"))
        superdev = graph.get_entity("SuperDev")
        assert superdev is not None
        assert superdev.entity_type == "project"
        assert len(graph.entities()) == 2
        assert len(graph.relations()) == 1
        assert graph.count() == {"entities": 2, "relations": 1}

    def test_add_relation_creates_entities(self) -> None:
        graph = KnowledgeGraph()
        graph.add_relation(Relation(source="A", target="B"))
        assert graph.count() == {"entities": 2, "relations": 1}

    def test_neighbors(self) -> None:
        graph = KnowledgeGraph()
        graph.add_relation(Relation(source="A", target="B"))
        graph.add_relation(Relation(source="A", target="C"))
        assert graph.neighbors("A") == ["B", "C"]
        assert "A" in graph.neighbors("B")

    def test_relations_filtered(self) -> None:
        graph = KnowledgeGraph()
        graph.add_relation(Relation(source="A", target="B"))
        graph.add_relation(Relation(source="C", target="D"))
        assert len(graph.relations("A")) == 1

    def test_clear(self) -> None:
        graph = KnowledgeGraph()
        graph.add_entity(Entity(name="X"))
        graph.clear()
        assert graph.count() == {"entities": 0, "relations": 0}


class TestGraphBuilder:
    def test_build_from_text(self) -> None:
        builder = GraphBuilder()
        graph = builder.build_from_text("O SuperDev usa Python para o agente.")
        assert len(graph.entities()) >= 1

    def test_build_from_documents(self) -> None:
        builder = GraphBuilder()
        documents = [
            Entity(name="ignored", entity_type="x"),
        ]
        # build_from_documents expects objects with .content; use simple stubs
        class StubDocument:
            content = "O SuperDev usa Python."

        graph = builder.build_from_documents([StubDocument()])
        assert len(graph.entities()) >= 1


class TestGraphSearch:
    def test_shortest_path_and_connected(self) -> None:
        search = GraphSearch()
        search.graph.add_relation(Relation(source="A", target="B"))
        search.graph.add_relation(Relation(source="B", target="C"))
        assert search.shortest_path("A", "C") == ["A", "B", "C"]
        assert search.connected("A", "C") is True
        assert search.connected("A", "Z") is False

    def test_reachable_and_expand(self) -> None:
        search = GraphSearch()
        search.graph.add_relation(Relation(source="A", target="B"))
        search.graph.add_relation(Relation(source="A", target="C"))
        assert search.expand("A") == ["B", "C"]
        assert search.reachable("A", depth=1) == ["B", "C"]

    def test_self_path(self) -> None:
        search = GraphSearch()
        assert search.shortest_path("A", "A") == ["A"]


class TestGraphTraversal:
    def test_bfs_dfs(self) -> None:
        traversal = GraphTraversal()
        traversal.graph.add_relation(Relation(source="A", target="B"))
        traversal.graph.add_relation(Relation(source="A", target="C"))
        traversal.graph.add_relation(Relation(source="B", target="D"))
        assert len(traversal.bfs("A")) == 4
        assert len(traversal.dfs("A")) == 4


class TestGraphMetrics:
    def test_degrees_and_most_connected(self) -> None:
        metrics = GraphMetrics()
        metrics.graph.add_relation(Relation(source="A", target="B"))
        metrics.graph.add_relation(Relation(source="A", target="C"))
        degrees = metrics.degrees()
        assert degrees["A"] == 2
        assert metrics.most_connected(1) == [("A", 2)]

    def test_isolated_and_density(self) -> None:
        metrics = GraphMetrics()
        metrics.graph.add_entity(Entity(name="alone"))
        metrics.graph.add_relation(Relation(source="A", target="B"))
        assert metrics.isolated() == ["alone"]
        assert metrics.density() > 0.0

    def test_density_single_entity(self) -> None:
        metrics = GraphMetrics()
        metrics.graph.add_entity(Entity(name="solo"))
        assert metrics.density() == 0.0


class TestKnowledgeGraphEngine:
    def test_add_text_and_related(self) -> None:
        engine = KnowledgeGraphEngine()
        engine.add_text("O SuperDev usa Python para buscas.")
        assert len(engine.graph.entities()) >= 1
        assert isinstance(engine.related("SuperDev"), list)

    def test_path_and_stats(self) -> None:
        engine = KnowledgeGraphEngine()
        engine.add_relation(Relation(source="A", target="B"))
        engine.add_relation(Relation(source="B", target="C"))
        assert engine.path("A", "C") == ["A", "B", "C"]
        stats = engine.stats()
        assert stats["entities"] >= 2
        assert "density" in stats
