"""Unit tests for the knowledge graph + semantic packages (phase 3).

Covers node/edge models, the graph builder (containment edges, import
resolution, dedupe, stats), the semantic engine (symbol index, file
classification, summary) and end-to-end pipeline integration where the
index stage runs both analyzers and stores results on the context.
"""
from __future__ import annotations

import pytest

from modules.ai_code_knowledge_graph.config.knowledge_config import KnowledgeConfig
from modules.ai_code_knowledge_graph.core.knowledge_context import KnowledgeContext
from modules.ai_code_knowledge_graph.core.knowledge_pipeline import KnowledgePipeline
from modules.ai_code_knowledge_graph.core.knowledge_runtime import KnowledgeRuntime
from modules.ai_code_knowledge_graph.graph import KnowledgeGraphBuilder
from modules.ai_code_knowledge_graph.graph.edges import make_edge
from modules.ai_code_knowledge_graph.graph.nodes import file_node_id, make_file_node, make_node, node_id
from modules.ai_code_knowledge_graph.semantic import SemanticEngine, SymbolIndex, classify_file


# ------------------------------------------------------------------ fixtures
def _entity(kind: str, name: str, start_line: int = 1, end_line: int | None = None, **extra) -> dict:
    return {"kind": kind, "name": name, "start_line": start_line, "end_line": end_line or start_line, **extra}


def _file_entry(rel_path: str, language: str, entities: list[dict]) -> dict:
    return {
        "rel_path": rel_path,
        "language": language,
        "size": 1,
        "parsed": {"language": language, "rel_path": rel_path, "entities": entities, "error": None},
    }


def _scan_fixture() -> dict:
    """A small scan result exercising every builder path."""
    files = [
        _file_entry("src/app.py", "python", [
            {"kind": "file", "name": "src/app.py", "start_line": 1, "end_line": 12, "line_count": 12},
            _entity("import", "helper", 1, source="src/helpers"),
            _entity("import", "helper", 1, source="src/helpers"),  # duplicate → deduped
            _entity("class", "App", 3, 12, bases=["Base"], methods=[
                _entity("method", "run", 4, 8, static=False),
            ]),
            _entity("function", "main", 10, 12),
            _entity("import", "missing", 2, source="pkg/not/here"),
        ]),
        _file_entry("src/helpers.py", "python", [
            {"kind": "file", "name": "src/helpers.py", "start_line": 1, "end_line": 3, "line_count": 3},
            _entity("function", "helper", 1, 3),
        ]),
        _file_entry("src/ui.js", "javascript", [
            {"kind": "file", "name": "src/ui.js", "start_line": 1, "end_line": 2, "line_count": 2},
            _entity("import", "util", 1, source="./util"),
            _entity("class", "Button", 2, 2),
        ]),
        _file_entry("src/util.js", "javascript", [
            {"kind": "file", "name": "src/util.js", "start_line": 1, "end_line": 1, "line_count": 1},
            _entity("function", "util", 1, 1),
        ]),
        _file_entry("db/schema.sql", "database", [
            {"kind": "file", "name": "db/schema.sql", "start_line": 1, "end_line": 4, "line_count": 4},
            _entity("table", "users", 1, 4, columns=["id", "email"]),
        ]),
        _file_entry("workflows/ci.yml", "workflow", [
            {"kind": "file", "name": "workflows/ci.yml", "start_line": 1, "end_line": 2, "line_count": 2},
            _entity("workflow", "CI", 1, 2, triggers=["push"], jobs=["build"], steps=1),
        ]),
        _file_entry("tests/test_app.py", "python", [
            {"kind": "file", "name": "tests/test_app.py", "start_line": 1, "end_line": 1, "line_count": 1},
            _entity("function", "test_main", 1, 1),
        ]),
    ]
    return {"project_root": "/tmp/demo", "files": files, "errors": [], "stats": {"files": len(files)}}


def _entities_by_id(graph) -> dict[str, dict]:
    return {node["id"]: node for node in graph["nodes"]}


def _edges_between(graph, source: str, relation: str) -> list[dict]:
    return [e for e in graph["edges"] if e["source"] == source and e["relation"] == relation]


# ---------------------------------------------------------------- node/edges
class TestGraphModels:
    def test_node_id_deterministic(self) -> None:
        assert node_id("class", "app.py", "App", 3) == "class:app.py:App:3"
        assert node_id("class", "app.py", "App", 3) == node_id("class", "app.py", "App", 3)
        assert file_node_id("src/app.py") == "file:src/app.py"

    def test_make_node_drops_none(self) -> None:
        node = make_node("function", "main", "app.py", 1, 5, params=["a"], doc=None)
        assert node["id"] == "function:app.py:main:1"
        assert node["start_line"] == 1
        assert node["end_line"] == 5
        assert node["params"] == ["a"]
        assert "doc" not in node

    def test_make_edge(self) -> None:
        edge = make_edge("a", "b", "imports", line=3, weight=2.0)
        assert edge == {"source": "a", "target": "b", "relation": "imports", "line": 3, "weight": 2.0}


# ------------------------------------------------------------ graph builder
class TestGraphBuilder:
    def test_file_nodes_for_every_file(self) -> None:
        graph = KnowledgeGraphBuilder().build(_scan_fixture())
        node_ids = set(_entities_by_id(graph))
        assert "file:src/app.py" in node_ids
        assert "file:db/schema.sql" in node_ids
        assert "file:workflows/ci.yml" in node_ids

    def test_contains_edges(self) -> None:
        graph = KnowledgeGraphBuilder().build(_scan_fixture())
        app_contains = _edges_between(graph, "file:src/app.py", "contains")
        contained = {e["target"] for e in app_contains}
        assert "class:src/app.py:App:3" in contained
        assert "function:src/app.py:main:10" in contained
        assert "import:src/app.py:helper:1" in contained

    def test_class_method_containment(self) -> None:
        graph = KnowledgeGraphBuilder().build(_scan_fixture())
        method_edges = _edges_between(graph, "class:src/app.py:App:3", "contains")
        assert [e["target"] for e in method_edges] == ["method:src/app.py:run:4"]
        method = _entities_by_id(graph)["method:src/app.py:run:4"]
        assert method["static"] is False

    def test_import_resolution(self) -> None:
        graph = KnowledgeGraphBuilder().build(_scan_fixture())
        assert _edges_between(graph, "file:src/app.py", "imports") == [
            {"source": "file:src/app.py", "target": "file:src/helpers.py", "relation": "imports", "line": 1, "weight": 1.0}
        ]
        assert _edges_between(graph, "file:src/ui.js", "imports") == [
            {"source": "file:src/ui.js", "target": "file:src/util.js", "relation": "imports", "line": 1, "weight": 1.0}
        ]

    def test_stats(self) -> None:
        graph = KnowledgeGraphBuilder().build(_scan_fixture())
        stats = graph["stats"]
        assert stats["node_count"] == len(graph["nodes"])
        assert stats["edge_count"] == len(graph["edges"])
        assert stats["nodes_by_kind"]["file"] == 7
        assert stats["nodes_by_kind"]["method"] == 1
        assert stats["nodes_by_kind"]["workflow"] == 1
        assert stats["edges_by_relation"]["contains"] >= 8
        assert stats["edges_by_relation"]["imports"] == 2

    def test_no_resolution_when_disabled(self) -> None:
        graph = KnowledgeGraphBuilder(resolve_imports=False).build(_scan_fixture())
        assert graph["stats"]["edges_by_relation"].get("imports", 0) == 0

    def test_index_stores_graph_on_context(self) -> None:
        config = KnowledgeConfig()
        ctx = KnowledgeContext(config=config)
        ctx.memory.put("scan_result", _scan_fixture())
        result = KnowledgeGraphBuilder().index(ctx)
        graph = ctx.memory.get("knowledge_graph")
        assert result["nodes"] == graph["stats"]["node_count"]
        assert ctx.stats["graph_nodes"] == graph["stats"]["node_count"]
        assert ctx.stats["graph_edges"] == graph["stats"]["edge_count"]


# -------------------------------------------------------------- semantic
class TestSemantic:
    def test_symbol_index_lookup(self) -> None:
        index = SymbolIndex.from_scan(_scan_fixture())
        assert index.lookup("helper") == [{"file": "src/helpers.py", "kind": "function", "line": 1}]
        assert index.lookup("App")[0]["kind"] == "class"
        assert index.lookup("users")[0]["kind"] == "table"
        assert index.lookup("nope") == []

    def test_symbol_index_excludes_imports(self) -> None:
        index = SymbolIndex.from_scan(_scan_fixture())
        # The import binding "helper" must not be a definition.
        assert index.lookup("helper")[0]["kind"] == "function"
        assert index.count() == 8  # helper, App, main, util, Button, users, CI, test_main

    def test_classify_file(self) -> None:
        assert classify_file("tests/test_app.py") == "test"
        assert classify_file("src/App.test.tsx") == "test"
        assert classify_file("config/settings.yaml") == "config"
        assert classify_file(".gitignore") == "config"
        assert classify_file("db/schema.sql") == "database"
        assert classify_file("migrations/0001_x.py") == "database"
        assert classify_file("src/services/user_service.py") == "service"
        assert classify_file("src/models/user.py") == "model"
        assert classify_file("src/plain.py") == "source"

    def test_analyze_summary(self) -> None:
        analysis = SemanticEngine().analyze(_scan_fixture())
        summary = analysis["summary"]
        assert summary["files"] == 7
        assert summary["symbols"] == 8
        assert summary["languages"]["python"] == 3
        assert summary["categories"]["test"] == 1
        assert summary["categories"]["database"] == 1
        assert "top_symbols" in summary

    def test_index_stores_analysis_on_context(self) -> None:
        config = KnowledgeConfig()
        ctx = KnowledgeContext(config=config)
        ctx.memory.put("scan_result", _scan_fixture())
        result = SemanticEngine().index(ctx)
        assert result["symbols"] == 8
        assert isinstance(ctx.memory.get("semantic_index"), SymbolIndex)
        assert ctx.memory.get("semantic_analysis")["languages"]["python"] == 3
        assert ctx.stats["semantic_symbols"] == 8


# --------------------------------------------------- pipeline + runtime wiring
class TestPipelineIntegration:
    def _config(self, root) -> KnowledgeConfig:
        config = KnowledgeConfig()
        config.scanner.project_root = str(root)
        config.scanner.project_dirs = ("src", "config", "docs", "workflows", "plugins", "db")
        config.scanner.scan_frontend = False
        return config

    def test_runtime_registers_phase_analyzers(self, tmp_path) -> None:
        config = self._config(tmp_path)
        runtime = KnowledgeRuntime(config)
        assert runtime.registry.has("analyzer", "graph")
        assert runtime.registry.has("analyzer", "semantic")

    def test_pipeline_index_stage_runs_analyzers(self, tmp_path) -> None:
        root = tmp_path / "fixture"
        (root / "src").mkdir(parents=True)
        (root / "src" / "app.py").write_text(
            "from lib import helper\n\ndef main():\n    return helper()\n", encoding="utf-8"
        )
        (root / "src" / "lib.py").write_text("def helper():\n    return 1\n", encoding="utf-8")

        config = self._config(root)
        ctx = KnowledgeContext(config=config)
        summary = KnowledgePipeline().run(ctx)

        index_stage = next(s for s in summary["stages"] if s["name"] == "index")
        assert index_stage["indexers"] == 5
        graph = ctx.memory.get("knowledge_graph")
        assert graph is not None
        assert graph["stats"]["node_count"] >= 4
        assert isinstance(ctx.memory.get("semantic_index"), SymbolIndex)
        assert ctx.stats["graph_nodes"] == graph["stats"]["node_count"]
        assert ctx.state.to_dict()["state"] == "ready"
