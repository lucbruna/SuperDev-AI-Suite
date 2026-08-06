"""Sandboxed test-runner validator for the ``test`` phase.

Runs the project's real test suite (pytest) inside :class:`SandboxRunner`
so the subprocess gets no shell, a sanitized environment, a strict timeout
and a capped output budget. A nonzero exit code fails the phase, which the
orchestrator turns into a failed session — the test gate.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from modules.autonomous_developer.core.exceptions import DeveloperError
from modules.autonomous_developer.execution.sandbox import SandboxConfig, SandboxRunner

__all__ = ["TestRunnerValidator", "parse_pytest_summary"]

_RE_PASSED = re.compile(r"(\d+)\s+passed")
_RE_FAILED = re.compile(r"(\d+)\s+failed")


def parse_pytest_summary(output: str) -> dict[str, int]:
    """Extract passed/failed counts from a pytest short summary."""
    return {
        "passed": int(_RE_PASSED.search(output).group(1)) if _RE_PASSED.search(output) else 0,
        "failed": int(_RE_FAILED.search(output).group(1)) if _RE_FAILED.search(output) else 0,
    }


class TestRunnerValidator:
    """Registered component for the ``test`` phase (kind "validator")."""

    def __init__(
        self,
        *,
        timeout_seconds: int = 300,
        max_output_bytes: int = 200_000,
        extra_args: tuple[str, ...] | None = None,
    ) -> None:
        self.extra_args = extra_args or ()
        self.sandbox = SandboxRunner(
            SandboxConfig(
                timeout_seconds=timeout_seconds,
                max_output_bytes=max_output_bytes,
            )
        )

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
        config = ctx.config
        if not config.run_tests:
            ctx.record("tests_skipped", 1)
            ctx.publish("test.skipped", {"goal": goal})
            return {"skipped": True, "passed": 0, "failed": 0}

        project_root = Path(config.project_root)
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--no-header",
            "-p",
            "no:cacheprovider",
            *self.extra_args,
        ]
        result = self.sandbox.run(command, cwd=project_root)
        output = result.combined
        counts = parse_pytest_summary(output)
        ctx.record("tests_passed", counts["passed"])
        ctx.record("tests_failed", counts["failed"])
        ctx.publish(
            "test.completed",
            {"returncode": result.returncode, **counts},
        )
        summary = {
            "passed": counts["passed"],
            "failed": counts["failed"],
            "returncode": result.returncode,
            "duration_seconds": result.duration_seconds,
            "output": output[-3000:],
            "truncated": result.truncated,
            "skipped": False,
        }
        if result.returncode != 0:
            raise DeveloperError(
                f"Repo tests failed: {counts['failed']} failed, {counts['passed']} passed",
                context={"returncode": result.returncode, "goal": goal},
            )
        return summary
