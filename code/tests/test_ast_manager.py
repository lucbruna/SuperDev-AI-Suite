from __future__ import annotations

from SuperDev.code.parsing.ast_manager import ASTManager

SAMPLE = """
import os
import json as j
from collections import OrderedDict
from . import helper
from ..pkg import util

class Greeter:
    def hello(self):
        return "hi"

class Farewell:
    pass

async def fetch():
    return 1

def helper_fn(x):
    return x * 2
"""


class TestASTManager:
    def test_initialization(self) -> None:
        mgr = ASTManager()
        assert mgr is not None

    def test_parse_extracts_imports(self) -> None:
        result = ASTManager().parse(SAMPLE)
        assert result is not None
        modules = [imp["module"] for imp in result["imports"]]
        assert modules == ["os", "json", "collections", "helper", "pkg"]

    def test_parse_import_metadata(self) -> None:
        result = ASTManager().parse(SAMPLE)
        assert result is not None
        os_imp = result["imports"][0]
        assert os_imp["asname"] is None
        assert os_imp["level"] == 0
        json_imp = result["imports"][1]
        assert json_imp["asname"] == "j"
        coll_imp = result["imports"][2]
        assert coll_imp["names"] == ["OrderedDict"]
        rel_imp = result["imports"][3]
        assert rel_imp["level"] == 1
        rel2_imp = result["imports"][4]
        assert rel2_imp["level"] == 2
        assert rel2_imp["names"] == ["util"]

    def test_parse_extracts_classes(self) -> None:
        result = ASTManager().parse(SAMPLE)
        assert result is not None
        assert result["classes"] == ["Greeter", "Farewell"]

    def test_parse_extracts_functions_including_async(self) -> None:
        result = ASTManager().parse(SAMPLE)
        assert result is not None
        assert "fetch" in result["functions"]
        assert "helper_fn" in result["functions"]

    def test_parse_returns_ast_tree(self) -> None:
        result = ASTManager().parse("x = 1\n")
        assert result is not None
        assert result["ast"] is not None
        assert result["ast"].body  # module-level statements

    def test_parse_syntax_error_returns_none(self) -> None:
        assert ASTManager().parse("def broken(:\n") is None

    def test_parse_empty_string(self) -> None:
        result = ASTManager().parse("")
        assert result is not None
        assert result["imports"] == []
        assert result["classes"] == []
        assert result["functions"] == []

    def test_to_dict_serializes_ast(self) -> None:
        mgr = ASTManager()
        tree = mgr.parse("import os\n")["ast"]
        serialized = mgr.to_dict(tree)
        assert serialized["type"] == "Module"
        assert any(field == "body" for field in serialized)

    def test_to_dict_plain_values(self) -> None:
        mgr = ASTManager()
        assert mgr.to_dict("x") == "x"
        assert mgr.to_dict(42) == 42
        assert mgr.to_dict(None) is None
        assert mgr.to_dict(["a", 1]) == ["a", 1]
