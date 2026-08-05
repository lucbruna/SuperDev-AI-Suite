"""REST endpoints for architecture intelligence.

Mirrors the Architecture Graph module's API shape: a dependency-less router
that calls the engine facade and returns plain dicts.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from modules.architecture_intelligence.api.deps import get_optional_user
from modules.architecture_intelligence.core.engine import get_intelligence

router = APIRouter()


@router.get("/")
def root(user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return {
        "module": "architecture_intelligence",
        "version": "1.0.0",
        "available": get_intelligence().available,
    }


@router.get("/metrics")
def metrics(user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().analyze()


@router.get("/insights")
def insights(limit: int | None = None, user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().insights(limit=limit)


@router.get("/plan")
def plan(user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().plan()


@router.get("/forecast")
def forecast(user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().forecast()


@router.get("/trends")
def trends(user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().trends()


@router.get("/optimize")
def optimize(user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().optimize()


@router.get("/diagnose")
def diagnose(user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().diagnose()


@router.get("/agents")
def agents(user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().agents()


@router.get("/history")
def history(limit: int = 20, user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().history_recent(limit=limit)


@router.post("/snapshot")
def snapshot(user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().snapshot()


@router.post("/ask")
def ask(payload: dict[str, Any], user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    question = (payload or {}).get("question", "")
    if not question:
        return {"available": False, "answer": "Missing 'question' in request body."}
    return get_intelligence().ask(question)


@router.get("/report")
def report(user: Any = Depends(get_optional_user)) -> dict[str, Any]:
    return get_intelligence().report()
