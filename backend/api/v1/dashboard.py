"""Dashboard aggregate endpoint.

Provides ``GET /system/dashboard`` returning, in a single call, everything
the admin dashboard home needs: KPIs, health, metrics, recent activity and
system metadata.

Unlike ``backend.api.v1.system``, this module does NOT depend on the
orchestrator being initialized: every data source is defensive and degrades
to zeros/empty values instead of failing.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.dependencies import get_current_active_user

logger = logging.getLogger("superdev.api.dashboard")

router = APIRouter(
    tags=["dashboard"],
    dependencies=[Depends(get_current_active_user)],
)


async def _count(db: AsyncSession, table: str) -> int:
    """Defensively count rows in a table. Never raises."""
    try:
        result = await db.execute(sa_text(f"SELECT COUNT(*) FROM {table}"))
        return int(result.scalar() or 0)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("count %s failed: %s", table, exc)
        return 0


async def _executions_stats(db: AsyncSession) -> dict[str, Any]:
    """Aggregate execution stats from agent_executions + workflow_runs (defensive)."""
    stats: dict[str, Any] = {"today": 0, "total": 0, "success_rate": 0.0, "by_status": {}}
    try:
        result = await db.execute(
            sa_text(
                """
                SELECT status, COUNT(*) FROM workflow_runs
                GROUP BY status
                """
            )
        )
        by_status: dict[str, int] = {}
        for row in result.fetchall():
            by_status[str(row[0])] = int(row[1])
        result = await db.execute(
            sa_text(
                """
                SELECT status, COUNT(*) FROM agent_executions
                GROUP BY status
                """
            )
        )
        for row in result.fetchall():
            key = str(row[0])
            by_status[key] = by_status.get(key, 0) + int(row[1])

        total = sum(by_status.values())
        today = 0
        try:
            result = await db.execute(
                sa_text(
                    "SELECT COUNT(*) FROM workflow_runs WHERE created_at >= :start"
                ),
                {"start": datetime.now(UTC) - timedelta(days=1)},
            )
            today = int(result.scalar() or 0)
            result = await db.execute(
                sa_text(
                    "SELECT COUNT(*) FROM agent_executions WHERE created_at >= :start"
                ),
                {"start": datetime.now(UTC) - timedelta(days=1)},
            )
            today += int(result.scalar() or 0)
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("executions today failed: %s", exc)

        done = by_status.get("completed", 0)
        failed = by_status.get("failed", 0)
        success_rate = round((done / (done + failed) * 100), 2) if (done + failed) > 0 else 0.0
        stats = {"today": today, "total": total, "success_rate": success_rate, "by_status": by_status}
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("executions stats failed: %s", exc)
    return stats


async def _cost_stats(db: AsyncSession) -> dict[str, Any]:
    """Aggregate cost from agent_executions (defensive)."""
    cost: dict[str, Any] = {"today_usd": 0.0, "month_usd": 0.0, "total_usd": 0.0}
    try:
        month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        day_start = datetime.now(UTC) - timedelta(days=1)
        result = await db.execute(
            sa_text(
                """
                SELECT
                  COALESCE(SUM(cost_usd) FILTER (WHERE created_at >= :day_start), 0) AS today_usd,
                  COALESCE(SUM(cost_usd) FILTER (WHERE created_at >= :month_start), 0) AS month_usd,
                  COALESCE(SUM(cost_usd), 0) AS total_usd
                FROM agent_executions
                """
            ),
            {"day_start": day_start, "month_start": month_start},
        )
        row = result.fetchone()
        if row:
            cost = {
                "today_usd": round(float(row[0] or 0), 4),
                "month_usd": round(float(row[1] or 0), 4),
                "total_usd": round(float(row[2] or 0), 4),
            }
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("cost stats failed: %s", exc)
    return cost


async def _health() -> dict[str, Any]:
    """Run the shared health checker, degrade gracefully."""
    try:
        from backend.health import HealthChecker, HealthStatus

        checker = HealthChecker()
        results = await checker.check_all()
        checks: dict[str, Any] = {}
        statuses = []
        for name, res in results.items():
            checks[name] = {
                "status": res.status.value,
                "message": res.message,
                "latency_ms": res.latency_ms,
            }
            statuses.append(res.status)
        if HealthStatus.UNHEALTHY in statuses:
            overall = "unhealthy"
        elif HealthStatus.DEGRADED in statuses:
            overall = "degraded"
        else:
            overall = "healthy"
        return {"status": overall, "checks": checks}
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("health check failed: %s", exc)
        return {"status": "unknown", "checks": {}}


async def _metrics() -> dict[str, Any]:
    """Read the in-process metrics collector (defensive)."""
    try:
        from backend.observability.metrics import get_metrics_collector

        m = get_metrics_collector().get_metrics()
        return {
            "uptime_seconds": m.get("uptime_seconds", 0),
            "total_requests": m.get("total_requests", 0),
            "total_errors": m.get("total_errors", 0),
            "error_rate_pct": m.get("error_rate_pct", 0),
            "requests_by_endpoint": m.get("requests_by_endpoint", {}),
        }
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("metrics read failed: %s", exc)
        return {
            "uptime_seconds": 0,
            "total_requests": 0,
            "total_errors": 0,
            "error_rate_pct": 0,
            "requests_by_endpoint": {},
        }


async def _recent_activity(
    db: AsyncSession,
    user_id: str | None,
) -> list[dict[str, Any]]:
    """Merge in-memory notifications + audit_logs + workflow_runs into one feed."""
    activity: list[dict[str, Any]] = []

    # In-memory notification manager (matches /api/v1/notifications)
    try:
        from backend.notifications.notification_manager import notification_manager

        if user_id:
            for n in notification_manager.list_for_user(user_id)[:10]:
                activity.append(
                    {
                        "id": n.id,
                        "type": n.notification_type.value,
                        "title": n.title,
                        "message": n.message,
                        "actor": "Sistema",
                        "timestamp": n.created_at.isoformat(),
                    }
                )
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("notifications feed failed: %s", exc)

    # Audit logs from DB
    try:
        result = await db.execute(
            sa_text(
                """
                SELECT id, action, resource_type, resource_id, created_at
                FROM audit_logs
                ORDER BY created_at DESC
                LIMIT 10
                """
            )
        )
        for row in result.fetchall():
            action = str(row[1])
            resource = str(row[2])
            activity.append(
                {
                    "id": str(row[0]),
                    "type": action,
                    "title": f"{action} {resource}",
                    "message": f"{action} em {resource}" + (f" ({row[3]})" if row[3] else ""),
                    "actor": "Sistema",
                    "timestamp": row[4].isoformat() if row[4] else datetime.now(UTC).isoformat(),
                }
            )
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("audit feed failed: %s", exc)

    # Workflow runs from DB
    try:
        result = await db.execute(
            sa_text(
                """
                SELECT id, workflow_id, status, created_at
                FROM workflow_runs
                ORDER BY created_at DESC
                LIMIT 5
                """
            )
        )
        for row in result.fetchall():
            activity.append(
                {
                    "id": str(row[0]),
                    "type": "workflow_run",
                    "title": f"Workflow {str(row[1])[:8]}",
                    "message": f"Status: {row[2]}",
                    "actor": "Sistema",
                    "timestamp": row[3].isoformat() if row[3] else datetime.now(UTC).isoformat(),
                }
            )
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("workflow runs feed failed: %s", exc)

    activity.sort(key=lambda a: a["timestamp"], reverse=True)
    return activity[:20]


@router.get("/dashboard")
async def system_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Aggregate dashboard data: KPIs, health, metrics, activity, metadata."""
    # Agent count: DB-backed via AgentService (matches /api/v1/agents)
    agents_total = 0
    agents_active = 0
    try:
        from backend.services.agent_service import AgentService

        service = AgentService(db)
        agents, _ = await service.list_agents(page=1, page_size=1000)
        agents_total = len(agents)
        agents_active = sum(1 for a in agents if a.is_active)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("agent count failed: %s", exc)
        agents_total = await _count(db, "agents")

    exec_stats = await _executions_stats(db)
    cost_stats = await _cost_stats(db)

    try:
        from backend.constants import PROJECT_NAME, VERSION

        system_meta = {"version": VERSION, "name": PROJECT_NAME, "api_prefix": "/api/v1"}
    except Exception:  # pragma: no cover - defensive
        system_meta = {"version": "6.0.0", "name": "SuperDev", "api_prefix": "/api/v1"}

    return {
        "success": True,
        "data": {
            "kpis": {
                "organizations": await _count(db, "organizations"),
                "projects": await _count(db, "projects"),
                "workflows": await _count(db, "workflows"),
                "agents": agents_total,
                "active_agents": agents_active,
                "knowledge_bases": await _count(db, "knowledge_bases"),
                "plugins_installed": await _count(db, "plugins"),
                "executions_today": exec_stats["today"],
                "executions_total": exec_stats["total"],
                "success_rate": exec_stats["success_rate"],
                "cost_today_usd": cost_stats["today_usd"],
                "cost_month_usd": cost_stats["month_usd"],
            },
            "health": await _health(),
            "metrics": await _metrics(),
            "recent_activity": await _recent_activity(db, current_user.get("id")),
            "system": system_meta,
        },
    }
