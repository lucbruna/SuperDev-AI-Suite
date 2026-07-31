"""
Executive Dashboard — Volume 12 Data & Analytics Engine.

Builds a functional executive dashboard from agent + project metrics:

    1. BIEngine         → 5 executive KPIs (projects, dev time, errors, costs, agent performance)
    2. VisualizationEngine → bar / line / pie / gauge chart specs
    3. ReportEngine     → executive report (markdown)

Outputs a self-contained HTML dashboard (inline SVG) + JSON spec + markdown report.

Run:
    cd SuperDev
    python examples/data-analytics/executive_dashboard.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Ensure the SuperDev repo root is importable when run as a script
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from data import DataConfig, DataEngine  # noqa: E402
from data.bi.executive_dashboard import ExecutiveDashboard  # noqa: E402
from data.data_models import DataBatch, DataRecord  # noqa: E402

OUTPUT_DIR = Path(__file__).parent / "output"


def _demo_agent_records() -> list[DataRecord]:
    """Simulated agent activity (duration, tokens, cost, status)."""
    data = [
        ("planner", 1200, 1800, 0.018, "completed"),
        ("coder", 24000, 5200, 0.052, "completed"),
        ("reviewer", 18000, 3100, 0.031, "completed"),
        ("coder", 150000, 9800, 0.098, "completed"),
        ("tester", 30000, 2600, 0.026, "failed"),
        ("deploy", 9000, 900, 0.009, "completed"),
        ("planner", 2100, 1500, 0.015, "completed"),
        ("reviewer", 45000, 4200, 0.042, "failed"),
    ]
    return [
        DataRecord(
            source="agent-activity",
            data={
                "agent": agent,
                "action": "run",
                "duration_ms": duration,
                "tokens_used": tokens,
                "cost": cost,
                "status": status,
            },
        )
        for agent, duration, tokens, cost, status in data
    ]


def _demo_project_records() -> list[DataRecord]:
    """Simulated project snapshots (status, tasks, errors, cost)."""
    data = [
        ("SuperDev Core", "completed", 12, 12, 3, 240.0),
        ("Mobile App", "active", 8, 14, 5, 180.0),
        ("Marketing Site", "completed", 6, 6, 1, 90.0),
        ("API Gateway", "active", 4, 9, 2, 130.0),
        ("Data Platform", "planning", 0, 15, 0, 40.0),
    ]
    return [
        DataRecord(
            source="project-snapshots",
            data={
                "project": name,
                "status": status,
                "tasks_completed": completed,
                "tasks_total": total,
                "errors": errors,
                "cost": cost,
            },
        )
        for name, status, completed, total, errors, cost in data
    ]


async def main() -> dict:
    engine = DataEngine(config=DataConfig.default())
    await engine.start()

    agent_records = _demo_agent_records()
    project_records = _demo_project_records()

    # Ingest + process (runs records through the pipeline)
    processed_agents = await engine.processing.process_batch(
        DataBatch(source="agent-activity", records=agent_records)
    )
    processed_projects = await engine.processing.process_batch(
        DataBatch(source="project-snapshots", records=project_records)
    )

    # Build the executive dashboard
    dashboard = ExecutiveDashboard(engine)
    result = await dashboard.build(
        agent_records=processed_agents.records,
        project_records=processed_projects.records,
    )

    # Render artifacts
    html = dashboard.render_html()
    json_spec = dashboard.render_json()

    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "executive_dashboard.html").write_text(html, encoding="utf-8")
    (OUTPUT_DIR / "executive_dashboard.json").write_text(json_spec, encoding="utf-8")
    (OUTPUT_DIR / "executive_report.md").write_text(
        result["report_markdown"], encoding="utf-8"
    )

    await engine.stop()

    return {
        "dashboard_id": result["dashboard_id"],
        "kpis": result["kpis"],
        "charts": len(result["charts"]),
        "html": str(OUTPUT_DIR / "executive_dashboard.html"),
        "json": str(OUTPUT_DIR / "executive_dashboard.json"),
        "report": str(OUTPUT_DIR / "executive_report.md"),
    }


if __name__ == "__main__":
    output = asyncio.run(main())
    print("\n=== Executive Dashboard — Output ===")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    print("\nKPIs:")
    for _key, info in output["kpis"].items():
        print(f"  {info['label']}: {info['value']} {info['unit']} [{info['status']}]")
