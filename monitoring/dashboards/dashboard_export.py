from __future__ import annotations

import csv
import io
import json
from typing import Any

from ..monitoring_models import DashboardWidget


class DashboardExport:
    """Exports dashboards to various formats."""

    @staticmethod
    def to_json(dashboard: Any, indent: int = 2) -> str:
        data = DashboardExport._dashboard_to_dict(dashboard)
        return json.dumps(data, indent=indent, default=str)

    @staticmethod
    def to_csv(dashboard: Any) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["widget_id", "title", "type", "metric", "position", "size"])
        for widget in dashboard.widgets:
            writer.writerow([
                widget.widget_id,
                widget.title,
                widget.widget_type,
                widget.metric,
                f"{widget.position}",
                f"{widget.size}",
            ])
        return output.getvalue()

    @staticmethod
    def to_html(dashboard: Any) -> str:
        lines = [
            "<!DOCTYPE html>",
            '<html><head><meta charset="utf-8">',
            "<title>Dashboard Export</title>",
            "<style>",
            "body { font-family: sans-serif; margin: 20px; }",
            "table { border-collapse: collapse; width: 100%; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background: #f5f5f5; }",
            "</style></head><body>",
            f"<h1>{dashboard.title}</h1>",
            f"<p>{dashboard.description}</p>",
            "<table>",
            "<tr><th>Widget</th><th>Type</th><th>Metric</th><th>Position</th></tr>",
        ]
        for widget in dashboard.widgets:
            lines.append(
                f"<tr><td>{widget.title}</td><td>{widget.widget_type}</td>"
                f"<td>{widget.metric}</td><td>{widget.position}</td></tr>"
            )
        lines.extend(["</table></body></html>"])
        return "\n".join(lines)

    @staticmethod
    def to_markdown(dashboard: Any) -> str:
        lines = [
            f"# {dashboard.title}",
            f"_{dashboard.description}_",
            "",
            "| Widget | Type | Metric |",
            "|--------|------|--------|",
        ]
        for widget in dashboard.widgets:
            lines.append(f"| {widget.title} | {widget.widget_type} | {widget.metric} |")
        lines.append("")
        lines.append(f"*Layout: {dashboard.layout}*")
        return "\n".join(lines)

    @staticmethod
    def _dashboard_to_dict(dashboard: Any) -> dict[str, Any]:
        return {
            "dashboard_id": dashboard.dashboard_id,
            "title": dashboard.title,
            "description": dashboard.description,
            "layout": dashboard.layout,
            "refresh_interval": dashboard.refresh_interval,
            "tags": dashboard.tags,
            "created_at": dashboard.created_at,
            "updated_at": dashboard.updated_at,
            "widgets": [
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
            ],
        }
