"""Tests for the shared safe dynamic-execution guard (core.safe_exec)."""

from __future__ import annotations

import pytest

from core.safe_exec import (
    guard_code_exec,
    safe_builtins,
    safe_exec,
    validate_import_statement,
)


class TestGuardCodeExec:
    def test_allows_safe_code(self) -> None:
        tree = guard_code_exec("x = 1\ny = x + 1\n")
        assert tree is not None

    def test_allows_loops_and_definitions(self) -> None:
        guard_code_exec(
            "def add(a, b):\n    return a + b\n"
            "result = add(1, 2)\n"
            "for i in range(3):\n    result += i\n")

    def test_blocks_import(self) -> None:
        with pytest.raises(ValueError, match="imports"):
            guard_code_exec("import os\n")

    def test_blocks_from_import(self) -> None:
        with pytest.raises(ValueError, match="imports"):
            guard_code_exec("from os import system\n")

    def test_blocks_dunder_attribute(self) -> None:
        with pytest.raises(ValueError, match="underscore attribute"):
            guard_code_exec("x = (1).__class__\n")

    def test_blocks_eval_call(self) -> None:
        with pytest.raises(ValueError, match="blocked"):
            guard_code_exec("eval('1+1')\n")

    def test_blocks_open_call(self) -> None:
        with pytest.raises(ValueError, match="blocked"):
            guard_code_exec("open('/etc/passwd')\n")

    def test_blocks_getattr_call(self) -> None:
        with pytest.raises(ValueError, match="blocked"):
            guard_code_exec("getattr(obj, '__class__')\n")

    def test_blocks_unknown_callable(self) -> None:
        with pytest.raises(ValueError, match="not allowed"):
            guard_code_exec("unknown_func(1)\n")


class TestSafeExec:
    def test_runs_and_returns_namespace(self) -> None:
        ns = safe_exec("result = 2 * 21\n")
        assert ns["result"] == 42

    def test_namespace_provided(self) -> None:
        ns = safe_exec("result = value + 1\n", {"value": 41})
        assert ns["result"] == 42

    def test_mutates_provided_namespace_in_place(self) -> None:
        # Regression: safe_exec must execute into the caller's dict (like
        # exec), so results written by the code are visible to the caller.
        ns: dict[str, object] = {}
        safe_exec("result = 42\n", ns)
        assert ns["result"] == 42

    def test_restricted_builtins_no_open(self) -> None:
        ns = safe_exec("")
        assert "open" not in ns["__builtins__"]
        assert "eval" not in ns["__builtins__"]
        assert "len" in ns["__builtins__"]

    def test_raises_on_malicious_code(self) -> None:
        with pytest.raises(ValueError):
            safe_exec("import os\n")


class TestSafeBuiltins:
    def test_returns_mapping(self) -> None:
        builtins = safe_builtins()
        assert isinstance(builtins, dict)
        assert "len" in builtins
        assert "open" not in builtins

    def test_extra_allowed(self) -> None:
        builtins = safe_builtins({"ascii"})
        assert "ascii" in builtins

    def test_hard_blocked_cannot_be_overridden(self) -> None:
        # "open" is hard-blocked even when requested via extra_allowed.
        builtins = safe_builtins({"open"})
        assert "open" not in builtins


class TestValidateImportStatement:
    def test_allows_safe_module(self) -> None:
        assert validate_import_statement("import json\n") == "import json\n"

    def test_allows_from_import(self) -> None:
        assert validate_import_statement("from math import sqrt\n") == \
            "from math import sqrt\n"

    def test_blocks_os(self) -> None:
        with pytest.raises(ValueError, match="not allowed"):
            validate_import_statement("import os\n")

    def test_blocks_non_import_statement(self) -> None:
        with pytest.raises(ValueError, match="unsupported statement"):
            validate_import_statement("x = 1\n")
