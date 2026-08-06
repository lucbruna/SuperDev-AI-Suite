"""Tests for the frontend views (Phase I)."""
from __future__ import annotations

from modules.autonomous_developer.config import DeveloperConfig
from modules.autonomous_developer.core import DeveloperContext, DeveloperRegistry
from modules.autonomous_developer.frontend import DashboardBuilder, View, ViewRegistry


def make_context(tmp_path):
    return DeveloperContext(
        config=DeveloperConfig(project_root=tmp_path),
        registry=DeveloperRegistry(),
    )


class TestView:
    def test_render_with_body(self):
        view = View(name="v", title="Title", body="content")
        assert view.render == "# Title\n\ncontent"

    def test_render_without_body(self):
        view = View(name="v", title="Title")
        assert view.render == "# Title"


class TestViewRegistry:
    def test_register_get_names(self):
        registry = ViewRegistry()
        view = View(name="home", title="Home")
        registry.register(view)
        assert registry.get("home") is view
        assert registry.names() == ["home"]

    def test_get_missing_returns_default(self):
        registry = ViewRegistry()
        default = View(name="d", title="Default")
        assert registry.get("missing", default) is default
        assert registry.get("missing") is None


class TestDashboardBuilder:
    def test_build_with_stats_sorted(self, tmp_path):
        ctx = make_context(tmp_path)
        ctx.record("zebra", 1)
        ctx.record("alpha", 2)
        view = DashboardBuilder().build(ctx)
        assert view.name == "dashboard"
        assert view.title == "Dashboard"
        assert view.body == "- alpha: 2\n- zebra: 1"

    def test_build_without_stats(self, tmp_path):
        view = DashboardBuilder().build(make_context(tmp_path))
        assert view.body == "_no stats_"
