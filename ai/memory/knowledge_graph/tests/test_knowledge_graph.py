from __future__ import annotations

from ..knowledge_graph_engine import KnowledgeGraphEngine
from ..graph_node import GraphNode
from ..graph_edge import GraphEdge
from ..graph_query import GraphQuery
from ..graph_index import GraphIndex
from ..graph_traversal import GraphTraversal
from ..graph_serializer import GraphSerializer
from ..graph_validator import GraphValidator
from ..graph_statistics import GraphStatistics


class TestGraphNode:
    def test_create(self) -> None:
        n = GraphNode("n1", "Person", {"name": "Alice"})
        assert n.node_id == "n1"
        assert n.label == "Person"
        assert n.get_property("name") == "Alice"

    def test_set_property(self) -> None:
        n = GraphNode("n1", "Person")
        n.set_property("age", 30)
        assert n.get_property("age") == 30

    def test_to_dict(self) -> None:
        n = GraphNode("n1", "Person", {"name": "Alice"})
        d = n.to_dict()
        assert d["node_id"] == "n1"

    def test_from_dict(self) -> None:
        n = GraphNode.from_dict({"node_id": "n1", "label": "Person", "properties": {"name": "Alice"}})
        assert n.node_id == "n1"
        assert n.label == "Person"


class TestGraphEdge:
    def test_create(self) -> None:
        e = GraphEdge("e1", "n1", "n2", "knows", {"since": 2020})
        assert e.edge_id == "e1"
        assert e.source == "n1"
        assert e.target == "n2"
        assert e.relation == "knows"

    def test_to_dict(self) -> None:
        e = GraphEdge("e1", "n1", "n2", "knows")
        d = e.to_dict()
        assert d["relation"] == "knows"

    def test_from_dict(self) -> None:
        e = GraphEdge.from_dict({"edge_id": "e1", "source": "n1", "target": "n2", "relation": "knows"})
        assert e.relation == "knows"


class TestGraphQuery:
    def setup_method(self) -> None:
        self.query = GraphQuery()
        self.nodes = [
            GraphNode("n1", "Person", {"name": "Alice"}),
            GraphNode("n2", "Person", {"name": "Bob"}),
            GraphNode("n3", "City", {"name": "NYC"}),
        ]

    def test_filter_by_label(self) -> None:
        results = self.query.filter_by_label("Person").execute_nodes(self.nodes)
        assert len(results) == 2

    def test_filter_by_property(self) -> None:
        results = self.query.filter_by_property("name", "Alice").execute_nodes(self.nodes)
        assert len(results) == 1

    def test_limit(self) -> None:
        results = self.query.limit(1).execute_nodes(self.nodes)
        assert len(results) == 1

    def test_reset(self) -> None:
        self.query.filter_by_label("Person")
        self.query.reset()
        results = self.query.execute_nodes(self.nodes)
        assert len(results) == 3

    def test_execute_edges(self) -> None:
        edges = [GraphEdge("e1", "n1", "n2", "knows")]
        results = self.query.filter_by_relation("knows").execute_edges(edges)
        assert len(results) == 1


class TestGraphIndex:
    def setup_method(self) -> None:
        self.index = GraphIndex()
        self.n1 = GraphNode("n1", "Person", {"name": "Alice"})
        self.n2 = GraphNode("n2", "Person", {"name": "Bob"})
        self.n3 = GraphNode("n3", "City", {"name": "NYC"})

    def test_add_and_find_by_label(self) -> None:
        self.index.add_node(self.n1)
        self.index.add_node(self.n2)
        results = self.index.find_by_label("Person")
        assert len(results) == 2

    def test_find_by_property(self) -> None:
        self.index.add_node(self.n1)
        results = self.index.find_by_property("name", "Alice")
        assert len(results) == 1

    def test_remove_node(self) -> None:
        self.index.add_node(self.n1)
        self.index.remove_node(self.n1)
        assert len(self.index.find_by_label("Person")) == 0

    def test_clear(self) -> None:
        self.index.add_node(self.n1)
        self.index.clear()
        assert len(self.index.find_by_label("Person")) == 0


class TestGraphTraversal:
    def setup_method(self) -> None:
        self.traversal = GraphTraversal()
        self.nodes = {
            "n1": GraphNode("n1", "A"),
            "n2": GraphNode("n2", "B"),
            "n3": GraphNode("n3", "C"),
        }
        self.edges = [
            GraphEdge("e1", "n1", "n2", "connects"),
            GraphEdge("e2", "n2", "n3", "connects"),
        ]

    def test_bfs(self) -> None:
        result = self.traversal.bfs("n1", self.nodes, self.edges)
        assert len(result) == 3

    def test_dfs(self) -> None:
        result = self.traversal.dfs("n1", self.nodes, self.edges)
        assert len(result) == 3

    def test_find_path(self) -> None:
        path = self.traversal.find_path("n1", "n3", self.edges)
        assert len(path) == 3
        assert path[0] == "n1"
        assert path[-1] == "n3"

    def test_find_path_no_path(self) -> None:
        path = self.traversal.find_path("n1", "missing", self.edges)
        assert path == []

    def test_reset(self) -> None:
        self.traversal.bfs("n1", self.nodes, self.edges)
        self.traversal.reset()
        assert self.traversal.visited_count == 0


class TestGraphSerializer:
    def test_serialize_deserialize(self) -> None:
        nodes = [GraphNode("n1", "Person")]
        edges = [GraphEdge("e1", "n1", "n2", "knows")]
        data = GraphSerializer.serialize(nodes, edges)
        parsed = GraphSerializer.deserialize(data)
        assert len(parsed["nodes"]) == 1
        assert len(parsed["edges"]) == 1

    def test_node_to_dict(self) -> None:
        n = GraphNode("n1", "Person")
        d = GraphSerializer.node_to_dict(n)
        assert d["node_id"] == "n1"

    def test_edge_to_dict(self) -> None:
        e = GraphEdge("e1", "n1", "n2", "knows")
        d = GraphSerializer.edge_to_dict(e)
        assert d["relation"] == "knows"


class TestGraphValidator:
    def test_validate_node(self) -> None:
        assert GraphValidator.validate_node(GraphNode("n1", "Person"))
        assert not GraphValidator.validate_node("not_a_node")

    def test_validate_edge(self) -> None:
        assert GraphValidator.validate_edge(GraphEdge("e1", "n1", "n2", "knows"))
        assert not GraphValidator.validate_edge("not_an_edge")

    def test_validate_no_duplicate_nodes(self) -> None:
        nodes = [GraphNode("n1", "A"), GraphNode("n2", "B")]
        assert GraphValidator.validate_no_duplicate_nodes(nodes)
        nodes_bad = [GraphNode("n1", "A"), GraphNode("n1", "A")]
        assert not GraphValidator.validate_no_duplicate_nodes(nodes_bad)

    def test_validate_references(self) -> None:
        e = GraphEdge("e1", "n1", "n2", "knows")
        assert GraphValidator.validate_references(e, {"n1", "n2"})
        assert not GraphValidator.validate_references(e, {"n1"})


class TestGraphStatistics:
    def test_compute(self) -> None:
        nodes = [GraphNode("n1", "Person"), GraphNode("n2", "Person"), GraphNode("n3", "City")]
        edges = [GraphEdge("e1", "n1", "n2", "knows")]
        stats = GraphStatistics().compute(nodes, edges)
        assert stats["node_count"] == 3
        assert stats["edge_count"] == 1
        assert stats["labels"]["Person"] == 2
        assert stats["relations"]["knows"] == 1


class TestKnowledgeGraphEngine:
    def setup_method(self) -> None:
        self.engine = KnowledgeGraphEngine()

    def test_add_get_node(self) -> None:
        n = GraphNode("n1", "Person")
        self.engine.add_node(n)
        assert self.engine.get_node("n1") is n
        assert self.engine.node_count == 1

    def test_remove_node(self) -> None:
        self.engine.add_node(GraphNode("n1", "Person"))
        assert self.engine.remove_node("n1") is True
        assert self.engine.node_count == 0

    def test_add_edge(self) -> None:
        self.engine.add_edge(GraphEdge("e1", "n1", "n2", "knows"))
        assert self.engine.edge_count == 1

    def test_get_edges(self) -> None:
        self.engine.add_edge(GraphEdge("e1", "n1", "n2", "knows"))
        assert len(self.engine.get_edges("n1")) == 1
        assert len(self.engine.get_edges()) == 1

    def test_remove_edge(self) -> None:
        self.engine.add_edge(GraphEdge("e1", "n1", "n2", "knows"))
        assert self.engine.remove_edge("e1") is True
        assert self.engine.remove_edge("missing") is False

    def test_clear(self) -> None:
        self.engine.add_node(GraphNode("n1", "Person"))
        self.engine.add_edge(GraphEdge("e1", "n1", "n2", "knows"))
        self.engine.clear()
        assert self.engine.node_count == 0
        assert self.engine.edge_count == 0

    def test_to_dict(self) -> None:
        self.engine.add_node(GraphNode("n1", "Person"))
        d = self.engine.to_dict()
        assert d["node_count"] == 1
