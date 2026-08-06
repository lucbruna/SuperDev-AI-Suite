"""Sandbox: env sanitization, no-shell, timeout, output cap."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from modules.autonomous_developer.execution.sandbox import (
    SandboxConfig,
    SandboxError,
    SandboxRunner,
    sanitize_env,
)


@pytest.fixture()
def runner() -> SandboxRunner:
    return SandboxRunner(
        SandboxConfig(timeout_seconds=10, max_output_bytes=1000)
    )


def test_sanitize_env_drops_secrets(monkeypatch):
    monkeypatch.setenv("FAKE_API_KEY", "sk-secret-value")
    monkeypatch.setenv("SUPERDEV_AD_LLM_OPENAI_KEY", "sk-other")
    monkeypatch.setenv("AUTH_TOKEN", "tok-123")
    monkeypatch.setenv("PATH", os.environ.get("PATH", ""))
    env = sanitize_env()
    assert "FAKE_API_KEY" not in env
    assert "SUPERDEV_AD_LLM_OPENAI_KEY" not in env
    assert "AUTH_TOKEN" not in env
    assert "PATH" in env  # benign allowlist key kept
    assert env.get("PYTHONIOENCODING") == "utf-8"


def test_shell_string_command_rejected(runner):
    with pytest.raises(SandboxError, match="argument list"):
        runner.run("echo hello; rm -rf /")


def test_empty_command_rejected(runner):
    with pytest.raises(SandboxError, match="Empty"):
        runner.run([])


def test_timeout_enforced(runner):
    slow = [sys.executable, "-c", "import time; time.sleep(30)"]
    with pytest.raises(SandboxError, match="timed out"):
        runner.run(slow, timeout=1)


def test_output_capped(runner):
    noisy = [sys.executable, "-c", "print('x' * 100_000)"]
    result = runner.run(noisy)
    assert result.returncode == 0
    assert result.truncated is True
    assert len(result.stdout) <= 1000


def test_env_allowlist_applied_to_child(monkeypatch):
    monkeypatch.setenv("TOP_SECRET", "hunter2")
    sandbox = SandboxRunner(SandboxConfig(timeout_seconds=10))
    probe = (
        "import os; print(os.environ.get('TOP_SECRET', '<absent>'))"
    )
    result = sandbox.run([sys.executable, "-c", probe])
    assert result.returncode == 0
    assert "<absent>" in result.stdout


def test_run_ok_and_cwd(tmp_path: Path):
    marker = tmp_path / "marker.txt"
    marker.write_text("hi\n", encoding="utf-8")
    sandbox = SandboxRunner(SandboxConfig(timeout_seconds=10))
    result = sandbox.run(
        [sys.executable, "-c", "import pathlib; print(pathlib.Path('marker.txt').read_text())"],
        cwd=tmp_path,
    )
    assert result.returncode == 0
    assert "hi" in result.stdout
