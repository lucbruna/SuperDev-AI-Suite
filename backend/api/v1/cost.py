"""Cost endpoint for the admin dashboard.

Reads LLM usage/cost from ``agent_executions`` (cost_usd, tokens_used)
and falls back to the in-process metrics collector. Defensive by design.
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

logger = logging.getLogger("superdev.api.cost")

router = APIRouter(
    tags=["cost"],
    dependencies=[Depends(get_current_active_user)],
)


async def _sum(db: AsyncSession, column: str, since: datetime | None = None) -> float:
    try:
        if since is None:
            result = await db.execute(sa_text(f"SELECT COALESCE(SUM({column}), 0) FROM agent_executions"))
        else:
            result = await db.execute(
                sa_text(f"SELECT COALESCE(SUM({column}), 0) FROM agent_executions WHERE created_at >= :since"),
                {"since": since},
            )
        return round(float(result.scalar() or 0), 4)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("cost sum(%s) failed: %s", column, exc)
        return 0.0


async def _breakdown(db: AsyncSession, column: str) -> list[dict[str, Any]]:
    """Per-agent cost/token breakdown from the DB."""
    try:
        result = await db.execute(
            sa_text(
                f"""
                SELECT agent_id, COUNT(*) AS n, COALESCE(SUM({column}), 0) AS total
                FROM agent_executions
                GROUP BY agent_id
                ORDER BY total DESC
                LIMIT 10
                """
            )
        )
        return [
            {"agent_id": str(row[0]), "count": int(row[1]), "total": round(float(row[2]), 4)}
            for row in result.fetchall()
        ]
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("cost breakdown(%s) failed: %s", column, exc)
        return []


@router.get("/summary")
async def cost_summary(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Total / today / month spend."""
    month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    day_start = datetime.now(UTC) - timedelta(days=1)
    total = await _sum(db, "cost_usd")
    month = await _sum(db, "cost_usd", since=month_start)
    today = await _sum(db, "cost_usd", since=day_start)
    return {
        "success": True,
        "data": {
            "currency": "USD",
            "total_usd": total,
            "month_usd": month,
            "today_usd": today,
        },
    }


@router.get("/breakdown")
async def cost_breakdown(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Per-agent cost and usage breakdown."""
    return {
        "success": True,
        "data": {
            "by_agent": await _breakdown(db, "cost_usd"),
            "tokens_by_agent": await _breakdown(db, "tokens_used"),
        },
    }


@router.get("/usage")
async def cost_usage(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Request/token volume from the metrics collector + DB."""
    from backend.observability.metrics import get_metrics_collector

    metrics = get_metrics_collector().get_metrics()
    total_cost = await _sum(db, "cost_usd")
    total_tokens = await _sum(db, "tokens_used")
    return {
        "success": True,
        "data": {
            "total_requests": metrics.get("total_requests", 0),
            "total_errors": metrics.get("total_errors", 0),
            "error_rate_pct": metrics.get("error_rate_pct", 0),
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "uptime_seconds": metrics.get("uptime_seconds", 0),
        },
    }


@router.get("/forecast")
async def cost_forecast(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Simple run-rate projection for the current month."""
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month = await _sum(db, "cost_usd", since=month_start)

    days_in_month = 30
    day_of_month = max(now.day, 1)
    projected = round(month / day_of_month * days_in_month, 4) if day_of_month > 0 else 0.0
    avg_daily = round(month / day_of_month, 4) if day_of_month > 0 else 0.0

    # Trend: compare first half vs second half of month so far (defensive)
    midpoint = month_start + timedelta(days=min(15, max(day_of_month // 2, 1)))
    first_half = await _sum(db, "cost_usd", since=month_start)
    second_half = await _sum(db, "cost_usd", since=midpoint)
    trend = "up" if second_half > first_half else ("down" if second_half < first_half else "flat")

    return {
        "success": True,
        "data": {
            "currency": "USD",
            "month_usd": month,
            "avg_daily_usd": avg_daily,
            "projected_month_usd": projected,
            "trend": trend,
        },
    }
