from __future__ import annotations

import html as _html
import json
from typing import Any

from .bi_engine import BIEngine


class DashboardBuilder:
    """Declarative dashboard composition toolkit.

    Builds BI dashboards from typed widgets (KPI cards, charts, tables and
    text panels), registers the result with the :class:`BIEngine` and renders
    it as self-contained HTML (stdlib-only, CSS grid) or JSON.
    """

    def __init__(
        self,
        bi: BIEngine | None = None,
        name: str = "Dashboard",
        owner: str = "",
        columns: int = 3,
    ) -> None:
        self.bi = bi
        self.name = name
        self.owner = owner
        self.columns = max(1, min(6, columns))
        self._widgets: list[dict[str, Any]] = []
        self._dashboard_id: str | None = None

    # -- widget registration -------------------------------------------------

    def add_kpi(
        self,
        label: str,
        value: float,
        unit: str = "",
        status: str = "neutral",
    ) -> DashboardBuilder:
        self._widgets.append({
            "type": "kpi",
            "label": label,
            "value": value,
            "unit": unit,
            "status": status,
        })
        return self

    def add_chart(
        self,
        title: str,
        chart_type: str,
        data: dict[str, Any],
    ) -> DashboardBuilder:
        self._widgets.append({
            "type": "chart",
            "title": title,
            "chart_type": chart_type,
            "data": dict(data),
        })
        return self

    def add_table(
        self,
        title: str,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> DashboardBuilder:
        self._widgets.append({
            "type": "table",
            "title": title,
            "columns": list(columns),
            "rows": [dict(r) for r in rows],
        })
        return self

    def add_text(self, title: str, content: str) -> DashboardBuilder:
        self._widgets.append({
            "type": "text",
            "title": title,
            "content": content,
        })
        return self

    # -- accessors -----------------------------------------------------------

    def widgets(self) -> list[dict[str, Any]]:
        return list(self._widgets)

    def widget_count(self) -> int:
        return len(self._widgets)

    def clear(self) -> int:
        count = len(self._widgets)
        self._widgets.clear()
        return count

    # -- engine integration --------------------------------------------------

    def build(self, bi: BIEngine | None = None) -> str:
        """Register the dashboard with the BI engine and return its id."""
        engine = bi or self.bi
        if engine is None:
            raise ValueError("No BIEngine available — pass one to build()")
        dashboard = engine.create_dashboard(self.name, owner=self.owner)
        self._dashboard_id = dashboard.dashboard_id
        for widget in self._widgets:
            title = widget.get("title", widget.get("label", "widget"))
            engine.add_widget(
                dashboard.dashboard_id,
                title,
                widget_type=widget.get("type", "chart"),
                metric=widget.get("label", ""),
            )
        return dashboard.dashboard_id

    def dashboard_id(self) -> str | None:
        return self._dashboard_id

    # -- rendering -----------------------------------------------------------

    def render_json(self) -> str:
        payload = {
            "name": self.name,
            "dashboard_id": self._dashboard_id,
            "columns": self.columns,
            "widgets": self._widgets,
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)

    def render_html(self) -> str:
        """Render a self-contained HTML dashboard (stdlib-only, CSS grid)."""
        status_colors = {
            "on_track": "#2ecc71",
            "good": "#2ecc71",
            "warning": "#f39c12",
            "behind": "#e74c3c",
            "bad": "#e74c3c",
            "neutral": "#3b82f6",
        }

        def style_for(status: str) -> str:
            return status_colors.get(status, "#95a5a6")

        # KPI cards are rendered separately for emphasis; other widgets flow in a grid.
        kpi_cards = []
        grid_cards = []
        for widget in self._widgets:
            if widget["type"] == "kpi":
                label = _html.escape(str(widget.get("label", "")))
                value = widget.get("value", 0)
                unit = _html.escape(str(widget.get("unit", "")))
                status = _html.escape(str(widget.get("status", "neutral")))
                color = style_for(widget.get("status", "neutral"))
                kpi_cards.append(
                    f'<div class="kpi-card" style="border-left: 4px solid {color}">'
                    f'<div class="kpi-label">{label}</div>'
                    f'<div class="kpi-value">{_html.escape(str(value))}'
                    f'<span class="kpi-unit"> {unit}</span></div>'
                    f'<div class="kpi-status">{status}</div></div>'
                )
            else:
                grid_cards.append(self._widget_to_html(widget))

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{_html.escape(self.name)} — SuperDev</title>
<style>
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; background: #f4f6f9; color: #1f2933; }}
    .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 24px 32px; }}
    .header h1 {{ margin: 0; font-size: 24px; }}
    .header p {{ margin: 4px 0 0; opacity: 0.85; }}
    .content {{ padding: 24px 32px; }}
    .kpi-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px; margin-bottom: 24px; }}
    .kpi-card {{ background: white; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    .kpi-label {{ font-size: 12px; color: #52606d; text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-value {{ font-size: 26px; font-weight: 700; margin: 6px 0; }}
    .kpi-unit {{ font-size: 14px; font-weight: 400; color: #7b8794; }}
    .kpi-status {{ font-size: 11px; color: #7b8794; }}
    .widget-grid {{ display: grid; grid-template-columns: repeat(var(--cols, 3), 1fr); gap: 16px; }}
    .widget {{ background: white; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    .widget h3 {{ margin: 0 0 12px; font-size: 14px; color: #3e4c59; }}
    .bar-chart {{ display: flex; align-items: flex-end; gap: 8px; height: 160px; }}
    .bar {{ background: #3b82f6; border-radius: 4px 4px 0 0; min-width: 24px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ text-align: left; padding: 6px 10px; border-bottom: 1px solid #e4e7eb; }}
    .text-panel {{ font-size: 13px; color: #52606d; line-height: 1.5; }}
    @media (max-width: 900px) {{ .widget-grid {{ grid-template-columns: 1fr 1fr; }} }}
    @media (max-width: 600px) {{ .widget-grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
    <div class="header">
        <h1>{_html.escape(self.name)}</h1>
        <p>SuperDev AI Suite — Volume 12 · BI Dashboard</p>
    </div>
    <div class="content">
        <div class="kpi-row">{"".join(kpi_cards)}</div>
        <div class="widget-grid" style="--cols: {self.columns}">{"".join(grid_cards)}</div>
    </div>
</body>
</html>"""

    def _widget_to_html(self, widget: dict[str, Any]) -> str:
        title = _html.escape(str(widget.get("title", widget.get("label", "Widget"))))
        widget_type = widget.get("type", "chart")
        if widget_type == "chart":
            return f'<div class="widget"><h3>{title}</h3>{self._chart_body(widget)}</div>'
        if widget_type == "table":
            return f'<div class="widget"><h3>{title}</h3>{self._table_body(widget)}</div>'
        if widget_type == "text":
            content = _html.escape(str(widget.get("content", "")))
            return f'<div class="widget"><h3>{title}</h3><div class="text-panel">{content}</div></div>'
        return f'<div class="widget"><h3>{title}</h3></div>'

    def _chart_body(self, widget: dict[str, Any]) -> str:
        data = widget.get("data", {})
        items = [(str(k), float(v)) for k, v in data.items() if isinstance(v, (int, float))]
        if not items:
            return "<p>Sem dados</p>"
        max_value = max(v for _, v in items) or 1.0
        bars = []
        for label, value in items:
            height = max(2.0, value / max_value * 100)
            bars.append(
                f'<div class="bar" style="height: {height:.1f}%" '
                f'title="{_html.escape(label)}: {value:.2f}"></div>'
            )
        return f'<div class="bar-chart">{"".join(bars)}</div>'

    def _table_body(self, widget: dict[str, Any]) -> str:
        columns = widget.get("columns", [])
        if not columns:
            return "<p>Sem dados</p>"
        header = "".join(f"<th>{_html.escape(str(c))}</th>" for c in columns)
        body = ""
        for row in widget.get("rows", []):
            cells = "".join(
                f"<td>{_html.escape(str(row.get(c, '')))}</td>" for c in columns
            )
            body += f"<tr>{cells}</tr>"
        return f'<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>'


__all__ = ["DashboardBuilder"]
