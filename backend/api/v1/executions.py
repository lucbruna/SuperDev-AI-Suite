"""Executions endpoint for the admin dashboard.

Aggregates workflow runs + agent executions from the database and the
in-memory agent manager. All queries are defensive: an unavailable table
or manager degrades to empty results instead of erroring.
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

logger = logging.getLogger("superdev.api.executions")

router = APIRouter(
    tags=["executions"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/stats/today")
async def executions_stats_today(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Execution stats scoped to the last 24h, plus running totals."""
    today = 0
    failed = 0
    running = 0
    by_status: dict[str, int] = {}
    start = datetime.now(UTC) - timedelta(days=1)

    # workflow_runs
    try:
        result = await db.execute(
            sa_text(
                """
                SELECT status, COUNT(*) FROM workflow_runs
                WHERE created_at >= :start
                GROUP BY status
                """
            ),
            {"start": start},
        )
        for row in result.fetchall():
            status = str(row[0])
            count = int(row[1])
            by_status[status] = by_status.get(status, 0) + count
            today += count
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("workflow_runs today failed: %s", exc)

    # agent_executions
    try:
        result = await db.execute(
            sa_text(
                """
                SELECT status, COUNT(*) FROM agent_executions
                WHERE created_at >= :start
                GROUP BY status
                """
            ),
            {"start": start},
        )
        for row in result.fetchall():
            status = str(row[0])
            count = int(row[1])
            by_status[status] = by_status.get(status, 0) + count
            today += count
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("agent_executions today failed: %s", exc)

    # In-memory agent manager may track runs too
    try:
        from backend.agents.agent_manager import agent_manager

        runs = getattr(agent_manager, "_executions", None) or []
        for run in runs:
            created = run.get("created_at") or run.get("started_at")
            if created:
                try:
                    if isinstance(created, datetime):
                        dt = created
                    else:
                        dt = datetime.fromisoformat(str(created))
                    if dt.replace(tzinfo=UTC) < start:
                        continue
                except (TypeError, ValueError):
                    pass
            status = str(run.get("status", "unknown"))
            by_status[status] = by_status.get(status, 0) + 1
            today += 1
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("agent_manager executions failed: %s", exc)

    failed = by_status.get("failed", 0)
    running = by_status.get("running", 0)
    success_rate = (
        round((today - failed - running) / today * 100, 2) if today > 0 else 0.0
    )

    return {
        "success": True,
        "data": {
            "count": today,
            "running": running,
            "failed": failed,
            "success_rate": success_rate,
            "by_status": by_status,
        },
    }


@router.get("")
async def list_executions(
    db: AsyncSession = Depends(get_db),
    limit: int = 25,
    offset: int = 0,
) -> dict[str, Any]:
    """Recent executions merged from DB runs and the in-memory manager."""
    items: list[dict[str, Any]] = []
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    # DB workflow runs
    try:
        result = await db.execute(
            sa_text(
                """
                SELECT id, workflow_id, status, trigger, triggered_by, created_at
                FROM workflow_runs
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            {"limit": limit, "offset": offset},
        )
        for row in result.fetchall():
            items.append(
                {
                    "id": str(row[0]),
                    "workflow_id": str(row[1]) if row[1] else None,
                    "status": str(row[2]),
                    "trigger": str(row[3]) if row[3] else None,
                    "triggered_by": str(row[4]) if row[4] else None,
                    "created_at": row[5].isoformat() if row[5] else None,
                }
            )
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("workflow runs list failed: %s", exc)

    # In-memory agent executions (fills gap when DB is empty)
    try:
        from backend.agents.agent_manager import agent_manager

        runs = getattr(agent_manager, "_executions", None) or []
        for run in runs[: max(1, limit - len(items))]:
            created = run.get("created_at") or run.get("started_at")
            items.append(
                {
                    "id": str(run.get("id", "")),
                    "workflow_id": None,
                    "agent_id": str(run.get("agent_id", "")),
                    "status": str(run.get("status", "unknown")),
                    "trigger": "manual",
                    "triggered_by": str(run.get("user_id", "")) or None,
                    "created_at": created.isoformat() if isinstance(created, datetime) else created,
                }
            )
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("agent executions list failed: %s", exc)

    items.sort(key=lambda item: item.get("created_at") or "", reverse=True)

    return {
        "success": True,
        "data": {"items": items[:limit], "total": len(items), "limit": limit, "offset": offset},
    }
