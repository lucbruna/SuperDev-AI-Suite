from __future__ import annotations

import json
from typing import Any

from ..monitoring_models import DashboardWidget


class DashboardRenderer:
    """Renders dashboard data into serializable formats."""

    @staticmethod
    def render_widget_data(widget: DashboardWidget, data: Any) -> dict[str, Any]:
        return {
            "widget_id": widget.widget_id,
            "title": widget.title,
            "widget_type": widget.widget_type,
            "metric": widget.metric,
            "position": list(widget.position),
            "size": list(widget.size),
            "data": data,
            "config": widget.config,
        }

    @staticmethod
    def render_json(dashboard: Any, widget_data: dict[str, Any] | None = None) -> str:
        result: dict[str, Any] = {
            "dashboard_id": dashboard.dashboard_id,
            "title": dashboard.title,
            "description": dashboard.description,
            "layout": dashboard.layout,
            "refresh_interval": dashboard.refresh_interval,
            "tags": dashboard.tags,
        }

        if widget_data:
            result["widgets"] = widget_data
        else:
            result["widgets"] = [
                {
                    "widget_id": w.widget_id,
                    "title": w.title,
                    "widget_type": w.widget_type,
                    "metric": w.metric,
                    "position": list(w.position),
                    "size": list(w.size),
                    "config": w.config,
                }
                for w in dashboard.widgets
            ]

        return json.dumps(result, indent=2, default=str)

    @staticmethod
    def render_html(dashboard: Any) -> str:
        lines = [
            "<!DOCTYPE html>",
            '<html><head><meta charset="utf-8">',
            f"<title>{dashboard.title}</title>",
            "<style>",
            "body { font-family: sans-serif; margin: 20px; background: #f5f5f5; }",
            ".dashboard { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }",
            ".widget { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }",
            ".widget h3 { margin: 0 0 8px; font-size: 14px; color: #666; }",
            ".widget .value { font-size: 28px; font-weight: bold; }",
            "</style></head><body>",
            f"<h1>{dashboard.title}</h1>",
            f"<p>{dashboard.description}</p>",
            '<div class="dashboard">',
        ]

        for widget in dashboard.widgets:
            lines.extend([
                '<div class="widget">',
                f"<h3>{widget.title}</h3>",
                f'<div class="value">--</div>',
                f"<small>{widget.metric}</small>",
                "</div>",
            ])

        lines.extend(["</div></body></html>"])
        return "\n".join(lines)
