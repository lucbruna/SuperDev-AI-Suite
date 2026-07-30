from __future__ import annotations

import pytest

from SuperDev.monitoring.dashboards.dashboard_manager import DashboardManager
from SuperDev.monitoring.dashboards.dashboard_widget import WidgetDefinition
from SuperDev.monitoring.dashboards.dashboard_renderer import DashboardRenderer
from SuperDev.monitoring.dashboards.dashboard_templates import DashboardTemplates
from SuperDev.monitoring.dashboards.dashboard_layout import DashboardLayout
from SuperDev.monitoring.dashboards.dashboard_refresh import DashboardRefresh
from SuperDev.monitoring.dashboards.dashboard_export import DashboardExport
from SuperDev.monitoring.dashboards.dashboard_share import DashboardShare
from SuperDev.monitoring.dashboards.dashboard_permissions import DashboardPermissions, DashboardRole


class TestDashboardManager:
    def test_create_dashboard(self) -> None:
        mgr = DashboardManager()
        mgr.create_dashboard(name="test", widgets=[])
        assert len(mgr._dashboards) == 1


class TestWidgetDefinition:
    def test_widget_defaults(self) -> None:
        w = WidgetDefinition(type="chart", title="CPU")
        assert w.type == "chart"


class TestDashboardTemplates:
    def test_system_template(self) -> None:
        tmpl = DashboardTemplates()
        dash = tmpl.system_dashboard()
        assert dash.name == "System Overview"


class TestDashboardLayout:
    def test_layout(self) -> None:
        layout = DashboardLayout(layout_type="grid")
        assert layout.layout_type == "grid"


class TestDashboardRefresh:
    def test_refresh(self) -> None:
        ref = DashboardRefresh(interval=30)
        assert ref.interval == 30
        ref.stop()


class TestDashboardExport:
    def test_json_export(self) -> None:
        exp = DashboardExport()
        data = exp.to_json({"name": "test"})
        assert '"name": "test"' in data


class TestDashboardShare:
    def test_share_link(self) -> None:
        share = DashboardShare()
        link = share.create_share_link("dash1", role="viewer")
        assert link is not None


class TestDashboardPermissions:
    def test_permissions(self) -> None:
        perm = DashboardPermissions()
        perm.set_role("user1", DashboardRole.EDITOR)
        assert perm.has_permission("user1", "edit")
