"""Tests for the command runner (Phase G)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.core.exceptions import ExecutionError
from modules.autonomous_developer.execution import CommandResult, CommandRunner


class TestCommandRunner:
    def test_dry_run_never_executes(self):
        result = CommandRunner().run("echo hello", dry_run=True)
        assert result.returncode == 0
        assert result.stdout == "DRY-RUN: echo hello"
        assert result.dry_run

    def test_real_run(self):
        result = CommandRunner().run('python -c "print(40 + 2)"')
        assert result.returncode == 0
        assert result.stdout.strip() == "42"

    def test_cwd_respected(self, tmp_path):
        (tmp_path / "probe.txt").write_text("x", encoding="utf-8")
        result = CommandRunner().run(
            "python -c \"import os; print(os.path.exists('probe.txt'))\"",
            cwd=tmp_path,
        )
        assert result.stdout.strip() == "True"

    def test_blocked_command_raises(self):
        with pytest.raises(ExecutionError):
            CommandRunner().run("rm -rf /")

    def test_blocked_command_raises_even_in_dry_run(self):
        with pytest.raises(ExecutionError):
            CommandRunner().run("rm -rf /", dry_run=True)

    def test_custom_deny_patterns(self):
        runner = CommandRunner(deny_patterns=["danger"])
        with pytest.raises(ExecutionError):
            runner.run("danger zone")

    def test_violations_list(self):
        runner = CommandRunner(deny_patterns=["rm -rf"])
        assert runner.violations("rm -rf everything") == ["rm -rf"]
        assert runner.violations("echo hi") == []

    def test_result_fields(self):
        result = CommandRunner().run('python -c "print(\'x\')"')
        assert isinstance(result, CommandResult)
        assert result.returncode == 0
        assert result.duration_seconds >= 0
        assert result.stderr == ""

    def test_custom_timeout_param_accepted(self):
        result = CommandRunner().run('python -c "print(1)"', timeout=10)
        assert result.returncode == 0
