"""Test-runner validator: sandboxed pytest execution and its gates."""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.exceptions import DeveloperError
from modules.autonomous_developer.validation.test_runner import (
    TestRunnerValidator,
    parse_pytest_summary,
)

PASSING_TEST = """\
def test_true():
    assert True


def test_also_true():
    assert 1 + 1 == 2


def test_third():
    assert "a" in "abc"
"""

FAILING_TEST = """\
def test_fail():
    assert False
"""


def _ctx(repo: Path, *, run_tests: bool = True) -> DeveloperContext:
    cfg = DeveloperConfig(project_root=str(repo), run_tests=run_tests)
    cfg.resolve()
    return DeveloperContext(config=cfg)


def _write(repo: Path, name: str, content: str) -> None:
    (repo / name).write_text(content, encoding="utf-8")


class TestParseSummary:
    def test_counts(self):
        out = "collected 4 items\n...F\n==== 1 failed, 3 passed in 0.5s ===="
        assert parse_pytest_summary(out) == {"passed": 3, "failed": 1}

    def test_no_tests(self):
        assert parse_pytest_summary("no tests ran") == {"passed": 0, "failed": 0}


class TestRunnerValidatorComponent:
    def test_passing_suite(self, tmp_path: Path):
        repo = tmp_path / "proj"
        repo.mkdir()
        _write(repo, "test_ok.py", PASSING_TEST)
        ctx = _ctx(repo)
        result = TestRunnerValidator(timeout_seconds=60).run(ctx, goal="goal")
        assert result["skipped"] is False
        assert result["passed"] >= 3
        assert result["failed"] == 0
        assert result["returncode"] == 0
        assert ctx.stats.get("tests_passed", 0) >= 3

    def test_failing_suite_raises(self, tmp_path: Path):
        repo = tmp_path / "proj"
        repo.mkdir()
        _write(repo, "test_bad.py", FAILING_TEST)
        ctx = _ctx(repo)
        with pytest.raises(DeveloperError, match="failed"):
            TestRunnerValidator(timeout_seconds=60).run(ctx, goal="goal")
        assert ctx.stats.get("tests_failed", 0) >= 1

    def test_skipped_when_run_tests_disabled(self, tmp_path: Path):
        repo = tmp_path / "proj"
        repo.mkdir()
        _write(repo, "test_bad.py", FAILING_TEST)
        ctx = _ctx(repo, run_tests=False)
        result = TestRunnerValidator().run(ctx, goal="goal")
        assert result["skipped"] is True
        assert ctx.stats.get("tests_skipped", 0) == 1

    def test_tooling_failure_raises_cleanly(self, tmp_path: Path):
        # Tooling failure (e.g. pytest unusable) fails the phase, not the loop.
        repo = tmp_path / "proj"
        repo.mkdir()
        _write(repo, "test_x.py", PASSING_TEST)
        ctx = _ctx(repo)
        validator = TestRunnerValidator(
            timeout_seconds=30, extra_args=("--this-option-does-not-exist",)
        )
        with pytest.raises(DeveloperError, match="tests failed"):
            validator.run(ctx, goal="goal")
