"""Tests for validation: syntax, security and the validator runner."""
from __future__ import annotations

from modules.self_healing_engine.tests.helpers import make_context
from modules.self_healing_engine.validation import (
    SecurityValidator,
    SyntaxValidator,
    ValidatorRunner,
)


def test_syntax_validator_passes_valid_python(tmp_path) -> None:
    ctx = make_context()
    path = tmp_path / "good.py"
    path.write_text("def f():\n    return 1\n", encoding="utf-8")

    result = SyntaxValidator().validate(str(path), ctx)
    assert result.passed is True


def test_syntax_validator_rejects_invalid_python(tmp_path) -> None:
    ctx = make_context()
    path = tmp_path / "bad.py"
    path.write_text("def f(:\n", encoding="utf-8")

    result = SyntaxValidator().validate(str(path), ctx)
    assert result.passed is False


def test_syntax_validator_skips_non_python() -> None:
    ctx = make_context()
    result = SyntaxValidator().validate("README.md", ctx)
    assert result.passed is True


def test_security_validator_detects_forbidden_pattern(tmp_path) -> None:
    ctx = make_context()
    path = tmp_path / "script.sh"
    path.write_text("#!/bin/sh\nrm -rf /\n", encoding="utf-8")

    result = SecurityValidator().validate(str(path), ctx)
    assert result.passed is False


def test_security_validator_rejects_protected_path() -> None:
    ctx = make_context()
    result = SecurityValidator().validate(".superdev/secret.txt", ctx)
    assert result.passed is False


def test_validator_runner_reports_and_publishes(tmp_path) -> None:
    ctx = make_context()
    path = tmp_path / "ok.py"
    path.write_text("x = 1\n", encoding="utf-8")

    runner = ValidatorRunner()
    results = runner.run(str(path), ctx)

    assert len(results) == 3
    assert all(r.passed for r in results)
    assert "validation.completed" in [e.type for e in ctx.events.history()]
