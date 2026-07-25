from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from {{project_name}}.config import get_settings
from {{project_name}}.database import get_db

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    settings = get_settings()
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready", tags=["health"])
async def readiness_check(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Readiness check with database connectivity."""
    settings = get_settings()
    
    # Check database
    db_healthy = False
    try:
        await db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        db_healthy = False
    
    healthy = db_healthy
    
    return {
        "status": "ready" if healthy else "not_ready",
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": {
            "database": "healthy" if db_healthy else "unhealthy",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/live", tags=["health"])
async def liveness_check() -> dict[str, Any]:
    """Liveness check."""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }