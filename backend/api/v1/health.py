from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    from backend.health import HealthChecker

    checker = HealthChecker()
    results = await checker.check_all()
    overall = all(r.status.value == "healthy" for r in results.values())
    return {
        "success": True,
        "data": {
            "status": "healthy" if overall else "degraded",
            "version": "5.0.0",
            "timestamp": datetime.now(UTC).isoformat(),
            "checks": {
                k: {"status": v.status.value, "latency_ms": v.latency_ms, "message": v.message}
                for k, v in results.items()
            },
        },
    }


@router.get("/health/ready")
async def readiness_check() -> dict:
    return {
        "status": "ok",
        "version": "5.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/alive")
async def liveness_check() -> dict:
    return {
        "status": "ok",
        "version": "5.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }
