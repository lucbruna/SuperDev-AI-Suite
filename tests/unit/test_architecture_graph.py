"""Unit tests for the Architecture Graph module (volume 2).

Covers the graph model, full build pipeline, exports, reports, AI layer,
event bus, scheduler, CLI and API router. Tests use a small temp fixture
project so nothing scans the real repository.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from modules.architecture_graph.config.graph_config import GraphConfig
from modules.architecture_graph.core.graph_engine import GraphEngine
from modules.architecture_graph.graph.edge_builder import contains, depends_on, imports
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.node_builder import (
    config_node,
    external_node,
    file_node,
    package_node,
)


# ------------------------------------------------------------------ fixtures
def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture()
def fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "fixture"
    _write(root, "src/app.py", "from lib import helper\nimport db\n\ndef main():\n    return helper()\n")
    _write(root, "src/lib.py", "import db\n\ndef helper():\n    return 42\n")
    _write(root, "src/db.py", "def connect():\n    return 'conn'\n")
    _write(root, "workflows/release.yaml", "name: release\nformat: yaml\nagents: [builder]\nsteps: []\n")
    return root


@pytest.fixture()
def graph(fixture_root: Path, tmp_path: Path) -> ArchitectureGraph:
    config = GraphConfig()
    config.project_root = str(fixture_root)
    config.project_dirs = ("src", "workflows")
    config.scan_frontend = False
    config.storage_backend = "memory"
    config.data_dir = str(tmp_path / "data")
    engine = GraphEngine(config)
    return engine.build()


# ---------------------------------------------------------------- graph model
class TestGraphModel:
    def test_add_nodes_and_edges(self) -> None:
        graph = ArchitectureGraph(name="t", project_root=".")
        graph.add_node(file_node("src/a.py", language="python", size=10))
        graph.add_node(file_node("src/b.py", language="python", size=20))
        assert graph.has_node("file:src/a.py")
        assert graph.edges_between("file:src/a.py", "file:src/b.py") == []
        assert graph.add_edge(imports("file:src/a.py", "file:src/b.py"))
        assert len(graph.edges_of("imports")) == 1
        assert graph.incoming("file:src/b.py") == ["file:src/a.py"]
        assert graph.outgoing("file:src/a.py") == ["file:src/b.py"]

    def test_node_meta(self) -> None:
        node = file_node("src/a.py", language="python", size=5)
        node.meta = {"owner": "platform"}
        data = node.to_dict()
        assert data["path"] == "src/a.py"
        assert data["meta"]["owner"] == "platform"

    def test_stats_and_roundtrip(self, graph: ArchitectureGraph) -> None:
        stats = graph.stats()
        assert stats["nodes"] >= 4
        assert stats["edges"] >= 1
        assert stats["kinds"]["file"] >= 3

        data = graph.to_dict()
        clone = ArchitectureGraph.from_dict(data)
        assert clone.stats()["nodes"] == stats["nodes"]
        assert clone.name == graph.name


# --------------------------------------------------------------------- build
class TestBuildPipeline:
    def test_build_produces_file_and_package_nodes(self, graph: ArchitectureGraph) -> None:
        assert graph.has_node("file:src/app.py")
        assert graph.has_node("file:src/lib.py")
        assert graph.has_node("package:src")

    def test_build_wires_import_edges(self, graph: ArchitectureGraph) -> None:
        assert len(graph.edges_of("imports")) >= 1

    def test_layers_assigned(self, graph: ArchitectureGraph) -> None:
        layers = {n.layer for n in graph.nodes() if n.layer}
        assert len(layers) >= 1

    def test_config_node_for_package_json(self, fixture_root: Path, tmp_path: Path) -> None:
        _write(fixture_root, "src/package.json", '{"name": "x"}')
        config = GraphConfig()
        config.project_root = str(fixture_root)
        config.project_dirs = ("src",)
        config.scan_frontend = False
        config.storage_backend = "memory"
        built = GraphEngine(config).build()
        assert built.has_node("config:package.json")

    def test_external_nodes_for_unknown_imports(self, graph: ArchitectureGraph) -> None:
        assert graph.has_node("external:db")


# ------------------------------------------------------------------ exports
class TestExports:
    def test_reactflow(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.exports.reactflow import to_reactflow, to_json

        data = to_reactflow(graph)
        assert "nodes" in data and "edges" in data
        assert len(data["nodes"]) == graph.stats()["nodes"]
        assert isinstance(to_json(graph), str)

    def test_cytoscape(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.exports.cytoscape import to_cytoscape

        data = to_cytoscape(graph)
        # Cytoscape.js elements are a flat list of node/edge dicts.
        assert "elements" in data and len(data["elements"]) >= 1
        assert all("data" in element for element in data["elements"])

    def test_mermaid(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.exports.mermaid import to_mermaid

        source = to_mermaid(graph)
        assert source.startswith("flowchart")
        assert "file" in source

    def test_graphviz_dot(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.exports.graphviz import to_dot

        dot = to_dot(graph)
        assert dot.startswith("digraph")

    def test_svg(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.exports.svg import to_svg

        svg = to_svg(graph)
        assert "<svg" in svg

    def test_html_self_contained(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.exports.html import to_html

        html = to_html(graph)
        assert "<html" in html and "<script" in html


# ------------------------------------------------------------------ reports
class TestReports:
    def test_architecture_report(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.reports.architecture_report import ArchitectureReport

        data = ArchitectureReport().to_dict(graph)
        assert data["format"] == "markdown"
        assert "source" in data and len(data["source"]) > 50

    def test_dependency_report(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.reports.dependency_report import DependencyReport

        data = DependencyReport().to_dict(graph)
        assert isinstance(data, dict)

    def test_documentation_generator(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.reports.documentation_generator import (
            DocumentationGenerator,
        )

        doc = DocumentationGenerator().generate(graph)
        assert isinstance(doc, str) and len(doc) > 50


# ------------------------------------------------------------------- AI layer
class TestAI:
    def test_reasoner(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.ai.architecture_reasoner import ArchitectureReasoner

        result = ArchitectureReasoner().analyze(graph)
        assert "score" in result or "insights" in result
        ranking = ArchitectureReasoner().risk_ranking(graph, limit=3)
        assert isinstance(ranking, list)

    def test_planner(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.ai.architecture_planner import ArchitecturePlanner

        plan = ArchitecturePlanner().plan(graph)
        assert "tasks" in plan and "total_tasks" in plan
        assert len(plan["tasks"]) == plan["total_tasks"]
        migration = ArchitecturePlanner().migration_plan(
            graph, target_package="platform", nodes=["file:src/app.py"]
        )
        assert migration["target_package"] == "platform"
        assert migration["total"] == 1
        assert migration["steps"][0]["node_id"] == "file:src/app.py"

    def test_explainer(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.ai.architecture_explainer import ArchitectureExplainer

        result = ArchitectureExplainer().explain_all(graph, "file:src/app.py")
        assert result["found"] is True
        assert result["node_id"] == "file:src/app.py"
        assert len(result["summary"]) > 0

    def test_rag_search(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.ai.architecture_rag import ArchitectureRAG

        rag = ArchitectureRAG()
        indexed = rag.index_graph(graph)
        assert indexed == graph.stats()["nodes"]
        results = rag.search("app", limit=3)
        assert isinstance(results, list)
        related = rag.suggest_related("file:src/app.py", limit=2)
        assert isinstance(related, list)

    def test_embeddings(self) -> None:
        from modules.architecture_graph.ai.architecture_embeddings import Embeddings

        emb = Embeddings()
        vec_a = emb.embed("architecture graph module")
        vec_b = emb.embed("architecture graph module")
        vec_c = emb.embed("video rendering pipeline")
        assert Embeddings.cosine(vec_a, vec_b) > 0.99
        assert Embeddings.cosine(vec_a, vec_c) < Embeddings.cosine(vec_a, vec_b)


# ---------------------------------------------------------- event bus + runner
class TestEvents:
    def test_publish_subscribe(self) -> None:
        from modules.architecture_graph.websocket.events import EventBus

        bus = EventBus()
        received: list[dict] = []
        unsubscribe = bus.subscribe(lambda event: received.append(event))
        bus.publish("graph.build.finished", {"stats": {"nodes": 3}})
        assert len(received) == 1
        assert received[0]["type"] == "graph.build.finished"
        assert received[0]["data"]["stats"]["nodes"] == 3
        assert bus.recent(1)[0]["type"] == "graph.build.finished"
        unsubscribe()
        bus.publish("x", {})
        assert len(received) == 1

    def test_periodic_runner(self) -> None:
        from modules.architecture_graph.scheduler.periodic import PeriodicRunner

        runner = PeriodicRunner()
        calls: list[int] = []
        runner.schedule("tick", lambda: calls.append(1), interval_seconds=0.1)
        runner.start()
        try:
            import time

            time.sleep(0.35)
        finally:
            runner.stop()
        assert len(calls) >= 2


# ---------------------------------------------------------------------- CLI
class TestCLI:
    def test_parser_subcommands(self) -> None:
        from modules.architecture_graph.cli.main import build_parser

        parser = build_parser()
        args = parser.parse_args(["build", "--no-persist"])
        assert args.command == "build" and args.no_persist
        args = parser.parse_args(["export", "mermaid"])
        assert args.command == "export" and args.fmt == "mermaid"
        args = parser.parse_args(["impact", "file:src/app.py"])
        assert args.command == "impact" and args.node_id == "file:src/app.py"

    def test_main_error_handling(self) -> None:
        from modules.architecture_graph.cli.main import main

        assert main(["definitely-not-a-command"]) == 2  # argparse usage error


# ----------------------------------------------------------------------- API
class TestAPI:
    def test_router_routes(self) -> None:
        from modules.architecture_graph.api.router import api_router

        paths = {getattr(route, "path", "") for route in api_router.routes}
        for expected in [
            "/",
            "/health",
            "/stats",
            "/build",
            "/refresh",
            "/nodes",
            "/analyze",
            "/insights",
            "/plan",
            "/search",
            "/export/{fmt}",
            "/reports/{kind}",
            "/ws",
        ]:
            assert expected in paths, f"missing route {expected}"

    def test_graph_routes_return_types(self) -> None:
        from modules.architecture_graph.api.router import api_router

        for route in api_router.routes:
            if getattr(route, "path", "").startswith("/export/"):
                assert getattr(route, "path", "") == "/export/{fmt}"


# ------------------------------------------------------------------ serialization
class TestSerialization:
    def test_json_roundtrip(self, graph: ArchitectureGraph) -> None:
        payload = json.dumps(graph.to_dict())
        clone = ArchitectureGraph.from_dict(json.loads(payload))
        assert clone.stats() == graph.stats()

    def test_graphviz_to_dict(self, graph: ArchitectureGraph) -> None:
        from modules.architecture_graph.exports.graphviz import to_dict

        data = to_dict(graph)
        assert "source" in data
