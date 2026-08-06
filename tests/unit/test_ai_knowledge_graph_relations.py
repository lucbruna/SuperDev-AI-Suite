"""Unit tests for phase 5 — relations, dependency analyzer and indexing.

Covers the relation resolver (endpoint validation, dependency/import queries),
the relation builder (derived depends_on + references edges), the dependency
resolver (transitive closures, impact sets, cycle detection), the dependency
analyzer hook and the composite knowledge indexer + index manager, plus the
pipeline wiring for the two new analyzers.
"""
from __future__ import annotations

import pytest

from modules.ai_code_knowledge_graph.config.knowledge_config import KnowledgeConfig
from modules.ai_code_knowledge_graph.core.knowledge_context import KnowledgeContext
from modules.ai_code_knowledge_graph.core.knowledge_runtime import KnowledgeRuntime
from modules.ai_code_knowledge_graph.dependency_analyzer import DependencyAnalyzer, DependencyResolver
from modules.ai_code_knowledge_graph.graph import KnowledgeGraphBuilder
from modules.ai_code_knowledge_graph.graph.edges import DEPENDS_ON, REFERENCES, make_edge
from modules.ai_code_knowledge_graph.graph.nodes import make_file_node, make_node
from modules.ai_code_knowledge_graph.indexing import IndexManager, KnowledgeIndexer
from modules.ai_code_knowledge_graph.relations import RelationBuilder, RelationResolver


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
    """Fixture with two resolved imports and no shared symbol names."""
    files = [
        _file_entry("src/app.py", "python", [
            {"kind": "file", "name": "src/app.py", "start_line": 1, "end_line": 12, "line_count": 12},
            _entity("import", "helper", 1, source="src/helpers"),
            _entity("class", "App", 3, 12),
            _entity("function", "main", 10, 12),
        ]),
        _file_entry("src/helpers.py", "python", [
            {"kind": "file", "name": "src/helpers.py", "start_line": 1, "end_line": 3, "line_count": 3},
            _entity("function", "helper", 1, 3),
        ]),
        _file_entry("src/lib.js", "javascript", [
            {"kind": "file", "name": "src/lib.js", "start_line": 1, "end_line": 2, "line_count": 2},
            _entity("import", "ui", 1, source="./ui"),
            _entity("function", "lib", 2, 2),
        ]),
        _file_entry("src/ui.js", "javascript", [
            {"kind": "file", "name": "src/ui.js", "start_line": 1, "end_line": 1, "line_count": 1},
            _entity("function", "ui", 1, 1),
        ]),
        _file_entry("tests/test_app.py", "python", [
            {"kind": "file", "name": "tests/test_app.py", "start_line": 1, "end_line": 1, "line_count": 1},
            _entity("function", "test_main", 1, 1),
        ]),
        _file_entry("db/schema.sql", "database", [
            {"kind": "file", "name": "db/schema.sql", "start_line": 1, "end_line": 4, "line_count": 4},
            _entity("table", "users", 1, 4),
        ]),
    ]
    return {"project_root": "/tmp/demo", "files": files, "errors": [], "stats": {"files": len(files)}}


def _graph() -> dict:
    return KnowledgeGraphBuilder().build(_scan_fixture())


def _cycle_graph() -> dict:
    nodes = [make_file_node("a.py"), make_file_node("b.py"), make_file_node("c.py")]
    edges = [
        make_edge("file:a.py", "file:b.py", "imports"),
        make_edge("file:b.py", "file:c.py", "imports"),
        make_edge("file:c.py", "file:a.py", "imports"),
    ]
    return {"project_root": "/tmp", "nodes": nodes, "edges": edges, "stats": {}}


def _shared_name_graph() -> dict:
    nodes = [
        make_file_node("a.py"),
        make_file_node("b.py"),
        make_node("function", "shared", "a.py", 1),
        make_node("function", "shared", "b.py", 1),
    ]
    return {"project_root": "/tmp", "nodes": nodes, "edges": [], "stats": {}}


def _indexed_context():
    config = KnowledgeConfig()
    ctx = KnowledgeContext(config=config)
    ctx.memory.put("scan_result", _scan_fixture())
    ctx.memory.put("knowledge_graph", _graph())
    return ctx


# ------------------------------------------------------------ relation resolver
class TestRelationResolver:
    def test_node_index(self) -> None:
        index = RelationResolver().node_index(_graph())
        assert "file:src/app.py" in index
        assert index["file:src/app.py"]["kind"] == "file"

    def test_resolve_no_dangling(self) -> None:
        report = RelationResolver().resolve(_graph())
        assert report["dangling_edges"] == []
        assert report["missing_node_ids"] == []

    def test_resolve_reports_dangling_edges(self) -> None:
        graph = _cycle_graph()
        graph["edges"].append(make_edge("file:a.py", "file:ghost.py", "imports"))
        report = RelationResolver().resolve(graph)
        assert len(report["dangling_edges"]) == 1
        assert report["missing_node_ids"] == ["file:ghost.py"]

    def test_dependencies_of(self) -> None:
        resolver = RelationResolver()
        assert resolver.dependencies_of(_graph(), "file:src/app.py") == ["file:src/helpers.py"]
        assert resolver.dependencies_of(_graph(), "file:src/lib.js") == ["file:src/ui.js"]

    def test_importers_of(self) -> None:
        resolver = RelationResolver()
        assert resolver.importers_of(_graph(), "file:src/helpers.py") == ["file:src/app.py"]
        assert resolver.importers_of(_graph(), "file:src/ui.js") == ["file:src/lib.js"]


# ------------------------------------------------------------- relation builder
class TestRelationBuilder:
    def test_depends_on_edges_derived_from_imports(self) -> None:
        edges = RelationBuilder().depends_on_edges(_graph())
        assert len(edges) == 2
        assert all(edge["relation"] == DEPENDS_ON for edge in edges)

    def test_depends_on_not_duplicated_when_present(self) -> None:
        graph = _graph()
        graph["edges"].append(make_edge("file:src/app.py", "file:src/helpers.py", DEPENDS_ON))
        assert len(RelationBuilder().depends_on_edges(graph)) == 1

    def test_reference_edges_for_shared_names(self) -> None:
        edges = RelationBuilder().reference_edges(_shared_name_graph())
        assert len(edges) == 2
        assert all(edge["relation"] == REFERENCES for edge in edges)
        sources = {edge["source"] for edge in edges}
        assert sources == {"file:a.py", "file:b.py"}

    def test_build_stats(self) -> None:
        result = RelationBuilder().build(_graph())
        assert result["stats"]["depends_on"] == 2
        assert result["stats"]["references"] == 0
        assert len(result["edges"]) == 2


# --------------------------------------------------------- dependency resolver
class TestDependencyResolver:
    def test_direct_dependencies(self) -> None:
        resolver = DependencyResolver(_graph())
        assert resolver.dependencies("file:src/app.py") == ["file:src/helpers.py"]
        assert resolver.dependencies("file:src/app.py", transitive=False) == ["file:src/helpers.py"]

    def test_transitive_dependencies(self) -> None:
        resolver = DependencyResolver(_cycle_graph())
        deps = resolver.dependencies("file:a.py")
        assert set(deps) == {"file:b.py", "file:c.py"}
        assert "file:b.py" in deps  # direct dependency present

    def test_impact(self) -> None:
        resolver = DependencyResolver(_cycle_graph())
        assert sorted(resolver.impact("file:a.py")) == ["file:b.py", "file:c.py"]
        acyclic = DependencyResolver(_graph())
        assert sorted(acyclic.impact("file:src/ui.js")) == ["file:src/lib.js"]

    def test_find_cycles(self) -> None:
        cycles = DependencyResolver(_cycle_graph()).find_cycles()
        assert len(cycles) == 1
        assert sorted(cycles[0]) == ["file:a.py", "file:b.py", "file:c.py"]

    def test_no_cycles_in_acyclic_graph(self) -> None:
        assert DependencyResolver(_graph()).find_cycles() == []


# -------------------------------------------------------- dependency analyzer
class TestDependencyAnalyzer:
    def test_analyze_report(self) -> None:
        report = DependencyAnalyzer().analyze(_graph())
        assert report["stats"]["files"] == 6
        assert report["stats"]["files_with_deps"] == 2
        assert report["stats"]["derived_edges"] == 2
        assert report["stats"]["cycles"] == 0
        entry = report["by_file"]["file:src/app.py"]
        assert entry["dependencies"] == ["file:src/helpers.py"]
        assert entry["impact"] == []

    def test_analyze_detects_cycles(self) -> None:
        report = DependencyAnalyzer().analyze(_cycle_graph())
        assert report["stats"]["cycles"] == 1

    def test_index_stores_analysis_on_context(self) -> None:
        ctx = _indexed_context()
        result = DependencyAnalyzer().index(ctx)
        assert result["files"] == 2
        assert ctx.memory.get("dependency_analysis")["stats"]["files_with_deps"] == 2
        assert ctx.stats["dependency_files"] == 2
        assert ctx.stats["dependency_edges"] == 2

    def test_index_skips_when_disabled(self) -> None:
        ctx = _indexed_context()
        ctx.config.run_relations = False
        result = DependencyAnalyzer().index(ctx)
        assert result["files"] == 0
        assert result["detail"] == "relations disabled"
        assert ctx.memory.get("dependency_analysis") is None


# ------------------------------------------------------------------- indexing
class TestKnowledgeIndexer:
    def test_index_builds_search_index(self) -> None:
        ctx = _indexed_context()
        result = KnowledgeIndexer().index(ctx)
        index = ctx.memory.get("search_index")
        assert index is not None
        assert result["items"] == index["stats"]["nodes"] == 15
        # 13 symbol keys: 6 file paths + 7 entity names (imports share names
        # with their functions, e.g. helper/ui).
        assert index["stats"]["symbols"] == 13
        assert ctx.stats["index_items"] == 15

    def test_query_finds_symbol(self) -> None:
        ctx = _indexed_context()
        KnowledgeIndexer().index(ctx)
        result = KnowledgeIndexer().query("App", ctx)
        assert len(result["symbols"]) == 1
        assert result["symbols"][0]["kind"] == "class"
        assert result["count"] == 1

    def test_query_without_index_is_empty(self) -> None:
        ctx = _indexed_context()
        result = KnowledgeIndexer().query("App", ctx)
        assert result["count"] == 0

    def test_index_skips_when_disabled(self) -> None:
        ctx = _indexed_context()
        ctx.config.run_indexing = False
        result = KnowledgeIndexer().index(ctx)
        assert result["items"] == 0
        assert ctx.memory.get("search_index") is None


class TestIndexManager:
    def test_default_registration(self) -> None:
        manager = IndexManager.default()
        assert manager.names == ["composite"]

    def test_build_all_and_stats(self) -> None:
        ctx = _indexed_context()
        manager = IndexManager.default()
        results = manager.build_all(ctx)
        assert results["composite"]["items"] == 15
        assert manager.stats(ctx)["nodes"] == 15

    def test_query_unknown_indexer_raises(self) -> None:
        with pytest.raises(KeyError):
            IndexManager.default().query("nope", "x", _indexed_context())


# ------------------------------------------------ pipeline wiring (phase 5)
class TestPipelineWiring:
    def test_runtime_registers_phase5_analyzers(self) -> None:
        runtime = KnowledgeRuntime(KnowledgeConfig())
        assert runtime.registry.has("analyzer", "relations")
        assert runtime.registry.has("analyzer", "indexer")
