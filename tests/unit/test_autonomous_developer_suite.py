"""Tests for the module-internal test helpers (Phase J)."""
from __future__ import annotations

from modules.autonomous_developer.core import DeveloperContext
from modules.autonomous_developer.tests import make_context, module_smoke


class TestMakeContext:
    def test_returns_fresh_context(self, tmp_path):
        ctx = make_context(project_root=tmp_path)
        assert isinstance(ctx, DeveloperContext)
        assert ctx.config.project_root == tmp_path
        assert ctx.artifacts == {}

    def test_fresh_registry_per_call(self, tmp_path):
        first = make_context(project_root=tmp_path)
        second = make_context(project_root=tmp_path)
        assert first.registry is not second.registry


class TestModuleSmoke:
    def test_all_components_construct_and_run(self, tmp_path):
        report = module_smoke(project_root=tmp_path)
        assert set(report) == {"planner", "generator", "reviewer", "agent"}
        for name, entry in report.items():
            assert entry == {"ok": True, "has_run": True}, name

    def test_deterministic_report(self, tmp_path):
        assert module_smoke(project_root=tmp_path) == module_smoke(
            project_root=tmp_path
        )
