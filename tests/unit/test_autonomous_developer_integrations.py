"""Tests for the dry-run integration clients (Phase G)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.integrations import (
    CIClient,
    GitClient,
    GitHubClient,
    IntegrationError,
    IntegrationResult,
    SlackNotifier,
)
from modules.autonomous_developer.core.exceptions import ExecutionError


class TestGitClient:
    def test_status_dry_run(self):
        result = GitClient().status()
        assert result.success
        assert result.tool == "git"
        assert result.action == "status"
        assert "[dry-run] git status" in result.output

    def test_commit_dry_run(self):
        assert GitClient().commit("initial").output == "[dry-run] git commit: initial"

    def test_diff_dry_run(self):
        assert "[dry-run] git diff" in GitClient().diff().output

    def test_commit_live_raises(self):
        with pytest.raises(IntegrationError):
            GitClient(dry_run=False).commit("x")

    def test_dry_run_flag_default(self):
        assert GitClient().dry_run is True


class TestGitHubClient:
    def test_create_pr(self):
        result = GitHubClient().create_pr("Add feature", body="details")
        assert result.tool == "github"
        assert result.action == "create_pr"
        assert "Add feature" in result.output

    def test_create_pr_live_raises(self):
        with pytest.raises(IntegrationError):
            GitHubClient(dry_run=False).create_pr("x")


class TestSlackNotifier:
    def test_notify(self):
        result = SlackNotifier().notify("deploys", "shipped")
        assert result.output == "[dry-run] slack #deploys: shipped"


class TestCIClient:
    def test_trigger(self):
        result = CIClient().trigger("build")
        assert result.output == "[dry-run] ci trigger: build"


class TestIntegrationError:
    def test_is_execution_error(self):
        assert issubclass(IntegrationError, ExecutionError)


class TestIntegrationResult:
    def test_defaults(self):
        result = IntegrationResult()
        assert result.success is True
        assert result.output == ""
        assert result.tool == ""
