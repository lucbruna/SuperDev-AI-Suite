from __future__ import annotations

import html as _html
import json
import statistics
from typing import Any

from ..data_models import KPI, DataRecord
from ..reporting.report_engine import ReportEngine
from ..visualization.visualization_engine import VisualizationEngine
from .bi_engine import BIEngine

# KPI identifiers (stable keys used by the dashboard and reports)
KPI_COMPLETED_PROJECTS = "completed_projects"
KPI_AVG_DEV_TIME = "avg_dev_time_min"
KPI_ERRORS = "total_errors"
KPI_COSTS = "total_cost"
KPI_AGENT_PERFORMANCE = "agent_performance_pct"

KPI_KEYS = [
    KPI_COMPLETED_PROJECTS,
    KPI_AVG_DEV_TIME,
    KPI_ERRORS,
    KPI_COSTS,
    KPI_AGENT_PERFORMANCE,
]


class ExecutiveDashboard:
    """Builds a functional executive dashboard from agent + project records.

    Combines the BI engine (executive KPIs), the visualization engine (chart
    specs) and the reporting engine (executive report) into a single artifact
    that can be rendered to HTML or JSON.
    """

    def __init__(
        self,
        engine: Any,
        bi: BIEngine | None = None,
        visualization: VisualizationEngine | None = None,
        reporting: ReportEngine | None = None,
    ) -> None:
        self.engine = engine
        self.bi = bi or engine.bi
        self.visualization = visualization or engine.visualization
        self.reporting = reporting or engine.reporting
        self._kpi_values: dict[str, dict[str, Any]] = {}
        self._kpi_targets: dict[str, float] = {
            KPI_COMPLETED_PROJECTS: 1.0,
            KPI_AVG_DEV_TIME: 30.0,      # minutes
            KPI_ERRORS: 5.0,             # lower is better
            KPI_COSTS: 100.0,            # USD
            KPI_AGENT_PERFORMANCE: 95.0,  # %
        }
        # KPIs whose status should be inverted (lower is better)
        self._lower_is_better: set[str] = {KPI_ERRORS}
        self._kpis: dict[str, KPI] = {}
        self._charts: list[dict[str, Any]] = []
        self._dashboard_id: str | None = None
        self._agent_records: list[DataRecord] = []
        self._project_records: list[DataRecord] = []

    # ------------------------------------------------------------------
    # KPI computation
    # ------------------------------------------------------------------

    def compute_kpis(
        self,
        agent_records: list[DataRecord],
        project_records: list[DataRecord],
    ) -> dict[str, dict[str, Any]]:
        """Compute the five executive KPIs from processed agent/project records."""
        completed = sum(
            1 for r in project_records
            if r.data.get("status") == "completed"
        )

        dev_times = [
            r.data["duration_ms"] for r in agent_records
            if isinstance(r.data.get("duration_ms"), (int, float))
        ]
        avg_dev_ms = statistics.mean(dev_times) if dev_times else 0.0

        errors = sum(
            int(r.data.get("errors", 0)) for r in project_records
            if isinstance(r.data.get("errors"), (int, float))
        )

        costs = sum(
            float(r.data.get("cost", 0.0)) for r in agent_records
            if isinstance(r.data.get("cost"), (int, float))
        )

        total_agents = len(agent_records)
        completed_agents = sum(
            1 for r in agent_records if r.data.get("status") == "completed"
        )
        performance = (completed_agents / total_agents * 100) if total_agents else 0.0

        self._kpi_values = {
            KPI_COMPLETED_PROJECTS: {
                "value": completed,
                "unit": "projetos",
                "label": "Projetos Concluídos",
            },
            KPI_AVG_DEV_TIME: {
                "value": round(avg_dev_ms / 60000, 1),
                "unit": "min",
                "label": "Tempo Médio de Dev",
            },
            KPI_ERRORS: {
                "value": errors,
                "unit": "erros",
                "label": "Erros",
            },
            KPI_COSTS: {
                "value": round(costs, 2),
                "unit": "USD",
                "label": "Custos",
            },
            KPI_AGENT_PERFORMANCE: {
                "value": round(performance, 1),
                "unit": "%",
                "label": "Performance dos Agentes",
            },
        }

        # Register KPIs in the BI engine and keep references on the instance.
        # Clean up any KPIs from a previous build to avoid orphans.
        for previous in self._kpis.values():
            self.bi.remove_kpi(previous.kpi_id)
        self._kpis.clear()
        for key in KPI_KEYS:
            info = self._kpi_values[key]
            kpi = self.bi.create_kpi(
                name=info["label"],
                metric=key,
                target=self._kpi_targets.get(key, 0.0),
                unit=info["unit"],
            )
            self.bi.update_kpi(kpi.kpi_id, info["value"])
            self._kpis[key] = kpi

        return self.kpi_snapshot()

    def kpi_snapshot(self) -> dict[str, dict[str, Any]]:
        """Return KPI values with status computed from the BI engine."""
        snapshot: dict[str, dict[str, Any]] = {}
        for key in KPI_KEYS:
            kpi = self._kpis.get(key)
            if kpi is None:
                continue
            info = self._kpi_values.get(key, {})
            value = info.get("value", 0.0)
            if key in self._lower_is_better:
                status = self._lower_is_better_status(key, value)
            else:
                status = self.bi.kpi_status(kpi)["status"]
            snapshot[key] = {
                "label": info.get("label", key),
                "value": value,
                "unit": info.get("unit", ""),
                "target": self._kpi_targets.get(key, 0.0),
                "status": status,
            }
        return snapshot

    def _lower_is_better_status(self, key: str, value: float) -> str:
        """Status for KPIs where lower values are better (e.g. errors)."""
        target = self._kpi_targets.get(key, 0.0)
        if target <= 0:
            return "no_target"
        if value <= target:
            return "on_track"
        if value <= target * 2:
            return "warning"
        return "behind"

    # ------------------------------------------------------------------
    # Visualization
    # ------------------------------------------------------------------

    def build_charts(
        self,
        _agent_records: list[DataRecord],
        project_records: list[DataRecord],
    ) -> list[dict[str, Any]]:
        """Build chart specs for the executive dashboard.

        ``_agent_records`` is accepted for API symmetry with :meth:`build`
        (the agent performance gauge is read from the computed KPI values).
        """
        # Cost per project (bar)
        cost_by_project: dict[str, float] = {}
        for record in project_records:
            project = record.data.get("project", "unknown")
            cost = record.data.get("cost", 0.0)
            if isinstance(cost, (int, float)):
                cost_by_project[project] = cost_by_project.get(project, 0.0) + cost

        # Tasks completed trend (line) — per project snapshot
        tasks_trend: dict[str, float] = {}
        for i, record in enumerate(project_records):
            tasks = record.data.get("tasks_completed", 0)
            if isinstance(tasks, (int, float)):
                tasks_trend[f"proj_{i + 1}"] = float(tasks)

        # Project status distribution (pie)
        status_dist: dict[str, int] = {}
        for record in project_records:
            status = record.data.get("status", "unknown")
            status_dist[str(status)] = status_dist.get(str(status), 0) + 1

        # Agent performance (gauge)
        performance = self._kpi_values.get(KPI_AGENT_PERFORMANCE, {}).get("value", 0.0)

        charts = [
            self.visualization.render_chart(
                "bar", cost_by_project, title="Custo por Projeto (USD)"
            ),
            self.visualization.render_chart(
                "line", tasks_trend, title="Tarefas Concluídas por Projeto"
            ),
            self.visualization.render_chart(
                "pie", status_dist, title="Distribuição de Status dos Projetos"
            ),
            self.visualization.render_chart(
                "gauge", {"performance": performance, "max": 100.0},
                title="Performance dos Agentes",
            ),
        ]
        return charts

    def build_dashboard(self) -> str:
        """Register a dashboard config and return its id."""
        dashboard = self.bi.create_dashboard("Executive Overview", owner="analytics")
        self._dashboard_id = dashboard.dashboard_id
        return dashboard.dashboard_id

    def _get_charts(self) -> list[dict[str, Any]]:
        """Return the charts built by :meth:`build`, re-rendering if unavailable."""
        if self._charts:
            return self._charts
        return self.build_charts(self._agent_records, self._project_records)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    async def generate_report(self) -> str:
        """Generate the executive report and return its rendered markdown."""
        kpi_snapshot = self.kpi_snapshot()
        report = await self.reporting.create_report(
            "Executive Dashboard Report",
            kind="executive",
            data={
                "kpis": kpi_snapshot,
                "completed_projects": kpi_snapshot.get(KPI_COMPLETED_PROJECTS, {}),
                "avg_dev_time": kpi_snapshot.get(KPI_AVG_DEV_TIME, {}),
                "total_errors": kpi_snapshot.get(KPI_ERRORS, {}),
                "total_cost": kpi_snapshot.get(KPI_COSTS, {}),
                "agent_performance": kpi_snapshot.get(KPI_AGENT_PERFORMANCE, {}),
                "recommendations": self._recommendations(kpi_snapshot),
            },
        )
        return self.reporting.render(report)

    def _recommendations(self, snapshot: dict[str, dict[str, Any]]) -> list[str]:
        recommendations: list[str] = []
        performance = snapshot.get(KPI_AGENT_PERFORMANCE, {}).get("value", 0.0)
        errors = snapshot.get(KPI_ERRORS, {}).get("value", 0)
        if performance < 95:
            recommendations.append(
                f"Performance dos agentes em {performance}% — revisar agentes lentos/falhos."
            )
        if errors and errors > 0:
            recommendations.append(f"{errors} erros detectados — priorizar correção de bugs.")
        costs = snapshot.get(KPI_COSTS, {}).get("value", 0.0)
        target = self._kpi_targets.get(KPI_COSTS, 100.0)
        if costs > target:
            recommendations.append(f"Custo {costs} USD acima da meta {target} USD — otimizar execução.")
        if not recommendations:
            recommendations.append("Nenhuma ação urgente identificada. Continue o bom trabalho.")
        return recommendations

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_html(self) -> str:
        """Render a self-contained HTML dashboard (stdlib-only, inline SVG)."""
        snapshot = self.kpi_snapshot()
        cards = []
        for key in KPI_KEYS:
            info = snapshot.get(key, {})
            status = info.get("status", "unknown")
            color = {
                "on_track": "#2ecc71",
                "warning": "#f39c12",
                "behind": "#e74c3c",
                "no_target": "#95a5a6",
            }.get(status, "#95a5a6")
            cards.append(
                f"""
                <div class="kpi-card" style="border-left: 4px solid {color}">
                    <div class="kpi-label">{_html.escape(str(info.get('label', key)))}</div>
                    <div class="kpi-value">{_html.escape(str(info.get('value', 0)))}
                        <span class="kpi-unit">{_html.escape(str(info.get('unit', '')))}</span></div>
                    <div class="kpi-status">{status}</div>
                </div>
                """
            )

        chart_html = "\n".join(self._chart_to_html(c) for c in self._get_charts())

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Executive Dashboard — SuperDev</title>
<style>
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; background: #f4f6f9; color: #1f2933; }}
    .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 24px 32px; }}
    .header h1 {{ margin: 0; font-size: 24px; }}
    .header p {{ margin: 4px 0 0; opacity: 0.85; }}
    .content {{ padding: 24px 32px; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px; margin-bottom: 24px; }}
    .kpi-card {{ background: white; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    .kpi-label {{ font-size: 12px; color: #52606d; text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-value {{ font-size: 28px; font-weight: 700; margin: 6px 0; }}
    .kpi-unit {{ font-size: 14px; font-weight: 400; color: #7b8794; }}
    .kpi-status {{ font-size: 11px; color: #7b8794; }}
    .chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }}
    .chart-card {{ background: white; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    .chart-card h3 {{ margin: 0 0 12px; font-size: 14px; color: #3e4c59; }}
    svg {{ width: 100%; height: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ text-align: left; padding: 6px 10px; border-bottom: 1px solid #e4e7eb; }}
</style>
</head>
<body>
    <div class="header">
        <h1>Executive Dashboard</h1>
        <p>SuperDev AI Suite — Volume 12 · Data & Analytics Engine</p>
    </div>
    <div class="content">
        <div class="kpi-grid">{"".join(cards)}</div>
        <div class="chart-grid">{chart_html}</div>
    </div>
</body>
</html>"""

    def _chart_to_html(self, spec: dict[str, Any]) -> str:
        title = _html.escape(str(spec.get("title", "Chart")))
        chart_type = spec.get("type", "")
        svg = ""
        if chart_type == "bar":
            svg = self._svg_bar(spec.get("data", {}))
        elif chart_type == "line":
            svg = self._svg_line(spec.get("points", []))
        elif chart_type == "pie":
            svg = self._svg_pie(spec.get("slices", []))
        elif chart_type == "gauge":
            svg = self._svg_gauge(spec.get("value", 0), spec.get("max", 100))
        elif chart_type == "table":
            svg = self._svg_table(spec)
        return f'<div class="chart-card"><h3>{title}</h3>{svg}</div>'

    @staticmethod
    def _svg_bar(data: dict[str, Any]) -> str:
        items = [(str(k), float(v)) for k, v in data.items() if isinstance(v, (int, float))]
        if not items:
            return "<p>Sem dados</p>"
        max_value = max(v for _, v in items) or 1.0
        bar_width = 100 / len(items)
        bars = []
        for i, (label, value) in enumerate(items):
            height = value / max_value * 100
            escaped = _html.escape(label)
            bars.append(
                f'<rect x="{i * bar_width + bar_width * 0.15:.1f}%" y="{100 - height:.1f}%" '
                f'width="{bar_width * 0.7:.1f}%" height="{height:.1f}%" fill="#3b82f6">'
                f'<title>{escaped}: {value:.2f}</title></rect>'
            )
        return (
            '<svg viewBox="0 0 100 100" preserveAspectRatio="none" '
            f'style="height:180px">{"".join(bars)}</svg>'
        )

    @staticmethod
    def _svg_line(points: list[dict[str, Any]]) -> str:
        values = [p.get("y") for p in points if isinstance(p.get("y"), (int, float))]
        if len(values) < 2:
            return "<p>Sem dados suficientes</p>"
        max_value = max(values) or 1.0
        coords = []
        for i, point in enumerate(points):
            x = i / (len(points) - 1) * 100
            y = 100 - (point["y"] / max_value * 100)
            coords.append(f"{x:.1f},{y:.1f}")
        polyline = " ".join(coords)
        return (
            '<svg viewBox="0 0 100 100" preserveAspectRatio="none" style="height:180px">'
            f'<polyline points="{polyline}" fill="none" stroke="#3b82f6" '
            'stroke-width="1.5"/></svg>'
        )

    @staticmethod
    def _svg_pie(slices: list[dict[str, Any]]) -> str:
        total = sum(s.get("value", 0) for s in slices)
        if total <= 0:
            return "<p>Sem dados</p>"
        colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]
        legend = []
        for i, slice_ in enumerate(slices):
            pct = slice_.get("value", 0) / total * 100
            color = colors[i % len(colors)]
            legend.append(
                f'<tr><td><span style="display:inline-block;width:10px;height:10px;'
                f'background:{color};border-radius:2px"></span> '
                f'{_html.escape(str(slice_.get("label", "")))}</td>'
                f'<td>{slice_.get("value", 0)} ({pct:.0f}%)</td></tr>'
            )
        return f'<table>{"".join(legend)}</table>'

    @staticmethod
    def _svg_gauge(value: float, maximum: float) -> str:
        pct = min(100, value / maximum * 100) if maximum else 0.0
        color = "#10b981" if pct >= 80 else ("#f59e0b" if pct >= 50 else "#ef4444")
        return (
            '<svg viewBox="0 0 100 20" preserveAspectRatio="none" style="height:30px">'
            f'<rect x="0" y="5" width="100" height="10" rx="5" fill="#e5e7eb"/>'
            f'<rect x="0" y="5" width="{pct:.1f}" height="10" rx="5" fill="{color}"/>'
            f'<text x="50" y="4" text-anchor="middle" font-size="7" fill="#1f2933">'
            f'{pct:.1f}%</text></svg>'
        )

    @staticmethod
    def _svg_table(spec: dict[str, Any]) -> str:
        columns = spec.get("columns", [])
        rows = spec.get("rows", [])
        if not columns:
            return "<p>Sem dados</p>"
        header = "".join(f"<th>{_html.escape(str(c))}</th>" for c in columns)
        body = ""
        for row in rows:
            cells = "".join(
                f"<td>{_html.escape(str(row.get(c, '')))}</td>" for c in columns
            )
            body += f"<tr>{cells}</tr>"
        return f'<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>'

    def render_json(self) -> str:
        """Render the dashboard as JSON (chart specs + KPIs)."""
        payload: dict[str, Any] = {
            "dashboard": self._dashboard_id,
            "kpis": self.kpi_snapshot(),
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # High-level builder
    # ------------------------------------------------------------------

    async def build(
        self,
        agent_records: list[DataRecord],
        project_records: list[DataRecord],
    ) -> dict[str, Any]:
        """Compute KPIs, build charts, register the dashboard and generate the report."""
        # Keep references for HTML rendering
        self._agent_records = list(agent_records)
        self._project_records = list(project_records)

        kpis = self.compute_kpis(agent_records, project_records)
        self._charts = self.build_charts(agent_records, project_records)
        dashboard_id = self.build_dashboard()
        report_md = await self.generate_report()
        charts = self._charts

        return {
            "dashboard_id": dashboard_id,
            "kpis": kpis,
            "charts": charts,
            "report_markdown": report_md,
        }


__all__ = [
    "ExecutiveDashboard",
    "KPI_COMPLETED_PROJECTS",
    "KPI_AVG_DEV_TIME",
    "KPI_ERRORS",
    "KPI_COSTS",
    "KPI_AGENT_PERFORMANCE",
    "KPI_KEYS",
]
