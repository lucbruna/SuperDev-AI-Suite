"""Unit tests for import resolution in ``CodeEngine.build_llm_context``.

Covers ``_module_to_path_map`` (module name -> file path, including package
``__init__.py`` -> package name) and ``_resolve_import_to_path`` (absolute
imports, ``from pkg import submodule``, and relative imports ``from . import
X`` / ``from ..pkg import Y``).
"""

from __future__ import annotations

from pathlib import Path

from SuperDev.code.code_engine import (
    _module_to_path_map,
    _rank_selection,
    _resolve_import_to_path,
)
from SuperDev.code.code_models import CodeFile
from SuperDev.code.understanding import SymbolIndex


class TestModuleToPathMap:
    def test_plain_module(self, tmp_path: Path) -> None:
        files = [CodeFile(path=str(tmp_path / "app" / "main.py"), content="")]
        mapping = _module_to_path_map(files, str(tmp_path))
        assert mapping["app.main"] == str(tmp_path / "app" / "main.py")

    def test_package_init(self, tmp_path: Path) -> None:
        files = [CodeFile(path=str(tmp_path / "app" / "__init__.py"), content="")]
        mapping = _module_to_path_map(files, str(tmp_path))
        assert mapping["app"] == str(tmp_path / "app" / "__init__.py")

    def test_nested_package_init(self, tmp_path: Path) -> None:
        files = [CodeFile(path=str(tmp_path / "app" / "sub" / "__init__.py"), content="")]
        mapping = _module_to_path_map(files, str(tmp_path))
        assert mapping["app.sub"] == str(tmp_path / "app" / "sub" / "__init__.py")

    def test_skips_files_outside_root(self, tmp_path: Path) -> None:
        files = [CodeFile(path=str(tmp_path / "other" / "x.py"), content="")]
        mapping = _module_to_path_map(files, str(tmp_path / "proj"))
        assert mapping == {}


class TestResolveImportToPath:
    def _files(self, root: Path) -> list[CodeFile]:
        return [
            CodeFile(path=str(root / "main.py"), content=""),
            CodeFile(path=str(root / "app" / "__init__.py"), content=""),
            CodeFile(path=str(root / "app" / "models.py"), content=""),
            CodeFile(path=str(root / "app" / "sub" / "__init__.py"), content=""),
            CodeFile(path=str(root / "app" / "sub" / "helper.py"), content=""),
        ]

    def test_absolute_import(self, tmp_path: Path) -> None:
        files = self._files(tmp_path)
        mapping = _module_to_path_map(files, str(tmp_path))
        imp = {"module": "app.models", "names": ["Model"], "level": 0}
        resolved = _resolve_import_to_path(Path("main.py"), imp, mapping)
        assert resolved == str(tmp_path / "app" / "models.py")

    def test_from_pkg_import_submodule(self, tmp_path: Path) -> None:
        # ``from app import models`` — the submodule wins over the __init__.
        files = self._files(tmp_path)
        mapping = _module_to_path_map(files, str(tmp_path))
        imp = {"module": "app", "names": ["models"], "level": 0}
        resolved = _resolve_import_to_path(Path("main.py"), imp, mapping)
        assert resolved == str(tmp_path / "app" / "models.py")

    def test_relative_dot_import(self, tmp_path: Path) -> None:
        # ``from . import helper`` inside app/sub/__init__.py (level 1).
        files = self._files(tmp_path)
        mapping = _module_to_path_map(files, str(tmp_path))
        imp = {"module": "helper", "names": ["helper"], "level": 1}
        resolved = _resolve_import_to_path(Path("app/sub/__init__.py"), imp, mapping)
        assert resolved == str(tmp_path / "app" / "sub" / "helper.py")

    def test_relative_dot_module_import(self, tmp_path: Path) -> None:
        # ``from .sub import x`` inside app/__init__.py (level 1).
        files = self._files(tmp_path)
        mapping = _module_to_path_map(files, str(tmp_path))
        imp = {"module": "sub", "names": ["x"], "level": 1}
        resolved = _resolve_import_to_path(Path("app/__init__.py"), imp, mapping)
        assert resolved == str(tmp_path / "app" / "sub" / "__init__.py")

    def test_relative_double_dot(self, tmp_path: Path) -> None:
        # ``from ..models import M`` inside app/sub/helper.py (level 2):
        # package app.sub, up one level -> app, then models -> app.models.
        files = self._files(tmp_path)
        mapping = _module_to_path_map(files, str(tmp_path))
        imp = {"module": "models", "names": ["M"], "level": 2}
        resolved = _resolve_import_to_path(Path("app/sub/helper.py"), imp, mapping)
        assert resolved == str(tmp_path / "app" / "models.py")

    def test_stdlib_import_returns_none(self, tmp_path: Path) -> None:
        files = self._files(tmp_path)
        mapping = _module_to_path_map(files, str(tmp_path))
        imp = {"module": "os", "names": [], "level": 0}
        assert _resolve_import_to_path(Path("main.py"), imp, mapping) is None

    def test_double_dot_at_root_returns_none(self, tmp_path: Path) -> None:
        # A root file cannot use ``from ..x import y`` — no parent package.
        files = self._files(tmp_path)
        mapping = _module_to_path_map(files, str(tmp_path))
        imp = {"module": "app", "names": [], "level": 2}
        assert _resolve_import_to_path(Path("main.py"), imp, mapping) is None


class TestRankSelection:
    """Tests for ``_rank_selection`` — query-symbol relevance ranking."""

    def test_empty_query_keeps_order_with_zero_relevance(self) -> None:
        index = SymbolIndex()
        index.add("Order", {"kind": "class", "path": "a.py"})
        selection = [{"path": "b.py", "depth": 1, "tokens": 10},
                     {"path": "a.py", "depth": 2, "tokens": 10}]
        ranked = _rank_selection(selection, index, None)
        assert [e["path"] for e in ranked] == ["b.py", "a.py"]
        assert all(e["relevance"] == 0 for e in ranked)

    def test_ranks_by_matched_symbol_weight(self) -> None:
        index = SymbolIndex()
        index.add("Order", {"kind": "class", "path": "a.py"})
        index.add("OrderItem", {"kind": "class", "path": "a.py"})
        index.add("OrderService", {"kind": "class", "path": "b.py"})
        index.add("create_order", {"kind": "function", "path": "b.py"})
        index.add("models.order", {"kind": "import", "path": "c.py"})
        selection = [{"path": "c.py", "depth": 1, "tokens": 10},
                     {"path": "b.py", "depth": 2, "tokens": 10},
                     {"path": "a.py", "depth": 3, "tokens": 10}]
        ranked = _rank_selection(selection, index, "Order")
        # a.py: 2 classes (6) > b.py: 1 class + 1 function (5) > c.py: 1 import (1)
        assert [e["path"] for e in ranked] == ["a.py", "b.py", "c.py"]
        assert ranked[0]["relevance"] == 6
        assert ranked[1]["relevance"] == 5
        assert ranked[2]["relevance"] == 1
        assert ranked[0]["matched_symbols"] == ["Order", "OrderItem"]

    def test_seeds_stay_first_even_when_less_relevant(self) -> None:
        index = SymbolIndex()
        index.add("Order", {"kind": "class", "path": "other.py"})
        selection = [{"path": "seed.py", "depth": 0, "tokens": 10},
                     {"path": "other.py", "depth": 1, "tokens": 10}]
        ranked = _rank_selection(selection, index, "Order")
        assert ranked[0]["path"] == "seed.py"
        assert ranked[1]["path"] == "other.py"
        assert ranked[1]["relevance"] == 3

    def test_case_insensitive_matching(self) -> None:
        index = SymbolIndex()
        index.add("order_total", {"kind": "function", "path": "a.py"})
        selection = [{"path": "a.py", "depth": 1, "tokens": 10}]
        ranked = _rank_selection(selection, index, "ORDER")
        assert ranked[0]["relevance"] == 2

    def test_unmatched_files_get_zero(self) -> None:
        index = SymbolIndex()
        index.add("Payment", {"kind": "class", "path": "a.py"})
        selection = [{"path": "a.py", "depth": 1, "tokens": 10},
                     {"path": "b.py", "depth": 2, "tokens": 10}]
        ranked = _rank_selection(selection, index, "Order")
        assert ranked[0]["path"] == "a.py"
        assert ranked[1]["path"] == "b.py"
        assert ranked[0]["relevance"] == 0
        assert ranked[1]["relevance"] == 0
