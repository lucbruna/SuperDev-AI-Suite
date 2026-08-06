"""FastAPI router exposing the AI Evolution Engine through the API.

Mounted by ``backend.app`` via ``_safe_include`` under
``/api/v1/evolution``, following the same convention as the
architecture-graph / architecture-intelligence / video-studio modules.

Every endpoint wraps the deterministic ``EvolutionAPI`` facade and returns
the backend's standard envelope ``{"success": bool, "data": ...}``.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException

from modules.ai_evolution_engine.api.evolution_api import EvolutionAPI
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_manager import EvolutionManager
from modules.ai_evolution_engine.integrations import build_default_registry

router = APIRouter(tags=["evolution"])

# Single in-process engine instance: deterministic, so state is safe to
# share across requests. Created lazily on first use.
_api: EvolutionAPI | None = None


def get_api() -> EvolutionAPI:
    global _api
    if _api is None:
        _api = EvolutionAPI(EvolutionManager(EvolutionContext()))
    return _api


def _ok(payload: dict[str, Any]) -> dict[str, Any]:
    """Unwrap facade response into the backend envelope."""
    if not payload.get("ok"):
        error = str(payload.get("error", "unknown error"))
        status = 404 if "not found" in error else 400
        raise HTTPException(status_code=status, detail=error)
    data = {k: v for k, v in payload.items() if k != "ok"}
    return {"success": True, "data": data}


@router.get("/status")
async def status() -> dict[str, Any]:
    return _ok(get_api().handle("status"))


@router.post("/analyze")
async def analyze() -> dict[str, Any]:
    return _ok(get_api().handle("analyze"))


@router.post("/recommend")
async def recommend(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return _ok(get_api().handle("recommend", body))


@router.post("/approve")
async def approve(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return _ok(get_api().handle("approve", body))


@router.post("/reject")
async def reject(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return _ok(get_api().handle("reject", body))


@router.post("/start")
async def start() -> dict[str, Any]:
    return _ok(get_api().handle("start"))


@router.post("/stop")
async def stop() -> dict[str, Any]:
    return _ok(get_api().handle("stop"))


@router.get("/integrations")
async def integrations() -> dict[str, Any]:
    return {"success": True, "data": build_default_registry().summary()}


@router.get("/dashboard")
async def dashboard() -> dict[str, Any]:
    from modules.ai_evolution_engine.frontend.dashboard_payload import DashboardPayload

    return {"success": True, "data": DashboardPayload(get_api()._manager).build()}
