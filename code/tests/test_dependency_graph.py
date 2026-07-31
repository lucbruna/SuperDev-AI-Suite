from __future__ import annotations

from SuperDev.code.code_models import CodeFile
from SuperDev.code.understanding.dependency_graph import DependencyGraph

FILES = [
    {"path": "src/app.py",
     "content": "import os\nfrom collections import OrderedDict\n"
                "import helpers.util\n"},
    {"path": "src/helpers/util.py",
     "content": "import json\n"},
    {"path": "src/broken.py",
     "content": "def broken(:\n"},
]


class TestDependencyGraph:
    def test_initialization(self) -> None:
        assert DependencyGraph() is not None

    def test_add_and_get_dependencies(self) -> None:
        graph = DependencyGraph()
        graph.add("a", "b")
        graph.add("a", "c")
        assert graph.get_dependencies("a") == ["b", "c"]
        assert graph.get_dependencies("missing") == []

    def test_add_deduplicates(self) -> None:
        graph = DependencyGraph()
        graph.add("a", "b")
        graph.add("a", "b")
        assert graph.get_dependencies("a") == ["b"]

    def test_get_dependents(self) -> None:
        graph = DependencyGraph()
        graph.add("a", "shared")
        graph.add("b", "shared")
        assert graph.get_dependents("shared") == ["a", "b"]
        assert graph.get_dependents("nobody") == []

    def test_nodes_and_edges(self) -> None:
        graph = DependencyGraph()
        graph.add("a", "b")
        graph.add("a", "c")
        assert sorted(graph.nodes()) == ["a"]
        assert sorted(graph.edges()) == [("a", "b"), ("a", "c")]

    def test_to_dict(self) -> None:
        graph = DependencyGraph()
        graph.add("a", "b")
        assert graph.to_dict() == {"a": ["b"]}

    def test_build_from_dict_files(self) -> None:
        graph = DependencyGraph()
        summary = graph.build(FILES)
        assert summary["files"] == 3
        assert summary["parsed"] == 2
        assert len(summary["errors"]) == 1
        assert summary["errors"][0]["path"] == "src/broken.py"
        deps = graph.get_dependencies("src/app.py")
        assert "os" in deps
        assert "collections" in deps
        assert "helpers.util" in deps
        assert graph.get_dependencies("src/helpers/util.py") == ["json"]

    def test_build_from_codefile_objects(self) -> None:
        files = [
            CodeFile(path="a.py", content="import os\n"),
            CodeFile(path="b.py", content="import a\n"),
        ]
        graph = DependencyGraph()
        summary = graph.build(files)
        assert summary["parsed"] == 2
        assert graph.get_dependencies("a.py") == ["os"]
        assert graph.get_dependencies("b.py") == ["a"]

    def test_build_edge_counts(self) -> None:
        graph = DependencyGraph()
        summary = graph.build(FILES)
        assert summary["nodes"] == 2
        assert summary["edges"] == 4  # app(3) + util(1)
