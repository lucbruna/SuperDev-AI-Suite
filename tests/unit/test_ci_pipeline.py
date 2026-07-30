"""Tests for CI/CD pipeline configuration files."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parent.parent.parent


class TestGitHubWorkflows:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.workflows_dir = _ROOT / ".github" / "workflows"

    def test_ci_workflow_exists(self):
        ci_path = self.workflows_dir / "ci.yml"
        assert ci_path.exists(), "ci.yml not found"

    def test_release_workflow_exists(self):
        release_path = self.workflows_dir / "release.yml"
        assert release_path.exists(), "release.yml not found"

    def test_ci_workflow_is_valid_yaml(self):
        ci_path = self.workflows_dir / "ci.yml"
        content = ci_path.read_text()
        parsed = yaml.safe_load(content)
        assert "name" in parsed
        # PyYAML parses `on:` as boolean True
        assert True in parsed or "on" in parsed
        assert "jobs" in parsed

    def test_release_workflow_is_valid_yaml(self):
        release_path = self.workflows_dir / "release.yml"
        content = release_path.read_text()
        parsed = yaml.safe_load(content)
        assert "name" in parsed
        assert True in parsed or "on" in parsed

    def test_ci_has_lint_job(self):
        ci_path = self.workflows_dir / "ci.yml"
        parsed = yaml.safe_load(ci_path.read_text())
        assert "lint" in parsed["jobs"]

    def test_ci_has_backend_test_job(self):
        ci_path = self.workflows_dir / "ci.yml"
        parsed = yaml.safe_load(ci_path.read_text())
        assert "test-backend" in parsed["jobs"]

    def test_ci_has_frontend_test_job(self):
        ci_path = self.workflows_dir / "ci.yml"
        parsed = yaml.safe_load(ci_path.read_text())
        assert "test-frontend" in parsed["jobs"]

    def test_ci_has_docker_build_job(self):
        ci_path = self.workflows_dir / "ci.yml"
        parsed = yaml.safe_load(ci_path.read_text())
        assert "docker-build" in parsed["jobs"]

    def test_ci_backend_tests_ignore_broken_files(self):
        ci_path = self.workflows_dir / "ci.yml"
        content = ci_path.read_text()
        assert "test_ai_router.py" in content
        assert "test_git_tool.py" in content


class TestCodeOwners:
    def test_codeowners_exists(self):
        path = _ROOT / ".github" / "CODEOWNERS"
        assert path.exists(), "CODEOWNERS not found"

    def test_codeowners_has_entries(self):
        path = _ROOT / ".github" / "CODEOWNERS"
        content = path.read_text()
        lines = [l for l in content.strip().split("\n") if l.strip() and not l.startswith("#")]
        assert len(lines) >= 3


class TestDependabot:
    def test_dependabot_exists(self):
        path = _ROOT / ".github" / "dependabot.yml"
        assert path.exists(), "dependabot.yml not found"

    def test_dependabot_is_valid_yaml(self):
        path = _ROOT / ".github" / "dependabot.yml"
        parsed = yaml.safe_load(path.read_text())
        assert "version" in parsed
        assert parsed["version"] == 2
        assert "updates" in parsed

    def test_dependabot_has_pip_and_npm(self):
        path = _ROOT / ".github" / "dependabot.yml"
        parsed = yaml.safe_load(path.read_text())
        ecosystems = {u["package-ecosystem"] for u in parsed["updates"]}
        assert "pip" in ecosystems
        assert "npm" in ecosystems
