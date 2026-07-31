from __future__ import annotations

from SuperDev.code.code_models import CodeFile
from SuperDev.code.parsing.ast_manager import ASTManager
from SuperDev.code.understanding.symbol_index import SymbolIndex


class TestSymbolIndex:
    def test_add_and_find(self) -> None:
        index = SymbolIndex()
        index.add("Greeter", {"kind": "class", "path": "a.py"})
        index.add("Greeter", {"kind": "class", "path": "b.py"})
        assert len(index.find("Greeter")) == 2
        assert index.find("missing") == []

    def test_add_deduplicates_same_location(self) -> None:
        index = SymbolIndex()
        index.add("x", {"kind": "function", "path": "a.py"})
        index.add("x", {"kind": "function", "path": "a.py"})
        assert len(index.find("x")) == 1

    def test_index_parsed(self) -> None:
        index = SymbolIndex()
        parsed = ASTManager().parse(
            "import os\nclass A: pass\nasync def f(): pass\n")
        assert parsed is not None
        index.index_parsed("mod.py", parsed)
        assert index.find("A") == [{"kind": "class", "path": "mod.py"}]
        assert index.find("f") == [{"kind": "function", "path": "mod.py"}]
        assert index.find("os") == [{"kind": "import", "path": "mod.py"}]

    def test_index_file(self) -> None:
        index = SymbolIndex()
        assert index.index_file("mod.py", "class A: pass\n") is True
        assert index.find("A")[0]["path"] == "mod.py"
        # Syntax error files are skipped.
        assert index.index_file("bad.py", "def broken(:\n") is False

    def test_index_files_accepts_codefile_and_dicts(self) -> None:
        index = SymbolIndex()
        files = [
            CodeFile(path="a.py", content="class A: pass\n"),
            {"path": "b.py", "content": "def b(): pass\n"},
            {"path": "bad.py", "content": "def broken(:\n"},
        ]
        parsed = index.index_files(files)
        assert parsed == 2
        assert "A" in index.symbols()
        assert "b" in index.symbols()
        assert "broken" not in index.symbols()

    def test_search_case_insensitive(self) -> None:
        index = SymbolIndex()
        index.index_file("a.py", "class UserProfile: pass\n")
        index.index_file("b.py", "def get_user(): pass\n")
        hits = dict(index.search("user"))
        assert "UserProfile" in hits
        assert "get_user" in hits
        assert index.search("zzz") == []

    def test_files_and_count(self) -> None:
        index = SymbolIndex()
        index.index_file("b.py", "def f(): pass\n")
        index.index_file("a.py", "class A: pass\n")
        assert index.files() == ["a.py", "b.py"]
        assert index.count() == 2

    def test_to_dict(self) -> None:
        index = SymbolIndex()
        index.index_file("a.py", "class A: pass\n")
        data = index.to_dict()
        assert "A" in data
        assert data["A"] == [{"kind": "class", "path": "a.py"}]


class TestSymbolRank:
    """Tests for the public relevance-ranking API ``SymbolIndex.rank``."""

    def test_rank_orders_by_kind_weight(self) -> None:
        index = SymbolIndex()
        index.add("user", {"kind": "class", "path": "a.py"})
        index.add("get_user", {"kind": "function", "path": "b.py"})
        index.add("user_api", {"kind": "import", "path": "c.py"})
        ranked = index.rank("user")
        assert [m["name"] for m in ranked] == ["user", "get_user", "user_api"]
        assert [m["relevance"] for m in ranked] == [3, 2, 1]

    def test_rank_aggregates_locations_per_symbol(self) -> None:
        index = SymbolIndex()
        index.add("User", {"kind": "class", "path": "a.py"})
        index.add("User", {"kind": "class", "path": "b.py"})
        index.add("get_user", {"kind": "function", "path": "c.py"})
        ranked = index.rank("user")
        assert ranked[0]["name"] == "User"
        assert ranked[0]["relevance"] == 6  # two class locations
        assert len(ranked[0]["locations"]) == 2

    def test_rank_case_insensitive(self) -> None:
        index = SymbolIndex()
        index.index_file("a.py", "class UserProfile: pass\n")
        names = [m["name"] for m in index.rank("USER")]
        assert names == ["UserProfile"]

    def test_rank_blank_query_matches_everything(self) -> None:
        index = SymbolIndex()
        index.index_file("a.py", "class A: pass\ndef f(): pass\n")
        ranked = index.rank("")
        assert {m["name"] for m in ranked} == {"A", "f"}

    def test_rank_no_match_returns_empty(self) -> None:
        index = SymbolIndex()
        index.index_file("a.py", "class User: pass\n")
        assert index.rank("zzz") == []

    def test_rank_stable_ties_keep_insertion_order(self) -> None:
        index = SymbolIndex()
        index.add("Alpha", {"kind": "class", "path": "a.py"})
        index.add("Beta", {"kind": "class", "path": "b.py"})
        index.add("Gamma", {"kind": "class", "path": "c.py"})
        ranked = index.rank("a")
        # All match "a" (lowercase), equal relevance -> insertion order.
        assert [m["name"] for m in ranked] == ["Alpha", "Beta", "Gamma"]
        assert all(m["relevance"] == 3 for m in ranked)
