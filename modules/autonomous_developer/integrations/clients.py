"""External tool integrations as deterministic dry-run clients.

Every client is a safe stub: with ``dry_run=True`` (the default) actions return
canned outputs and never touch a live system. With ``dry_run=False`` they raise
:class:`IntegrationError` because no live transport is configured, keeping the
suite hermetic.
"""
from __future__ import annotations

from dataclasses import dataclass

from modules.autonomous_developer.core.exceptions import ExecutionError

__all__ = [
    "CIClient",
    "GitClient",
    "GitHubClient",
    "IntegrationError",
    "IntegrationResult",
    "SlackNotifier",
]


class IntegrationError(ExecutionError):
    """Raised when a live integration action is attempted without a transport."""


@dataclass(slots=True)
class IntegrationResult:
    """Outcome of a tool action."""

    tool: str = ""
    action: str = ""
    output: str = ""
    success: bool = True


class _DryRunClient:
    """Base for clients that refuse live actions by default."""

    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    def _ensure(self) -> None:
        if not self.dry_run:
            raise IntegrationError(
                f"{type(self).__name__} has no live transport; use dry_run=True"
            )


class GitClient(_DryRunClient):
    def status(self) -> IntegrationResult:
        self._ensure()
        return IntegrationResult(
            tool="git", action="status", output="[dry-run] git status: clean"
        )

    def commit(self, message: str) -> IntegrationResult:
        self._ensure()
        return IntegrationResult(
            tool="git", action="commit", output=f"[dry-run] git commit: {message}"
        )

    def diff(self) -> IntegrationResult:
        self._ensure()
        return IntegrationResult(
            tool="git", action="diff", output="[dry-run] git diff: 0 changes"
        )


class GitHubClient(_DryRunClient):
    def create_pr(self, title: str, body: str = "") -> IntegrationResult:
        self._ensure()
        return IntegrationResult(
            tool="github",
            action="create_pr",
            output=f"[dry-run] PR: {title}",
        )


class SlackNotifier(_DryRunClient):
    def notify(self, channel: str, text: str) -> IntegrationResult:
        self._ensure()
        return IntegrationResult(
            tool="slack",
            action="notify",
            output=f"[dry-run] slack #{channel}: {text}",
        )


class CIClient(_DryRunClient):
    def trigger(self, pipeline: str) -> IntegrationResult:
        self._ensure()
        return IntegrationResult(
            tool="ci", action="trigger", output=f"[dry-run] ci trigger: {pipeline}"
        )
