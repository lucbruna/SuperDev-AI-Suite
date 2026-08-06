"""FastAPI router exposing the Digital Twin module through the API.

Mounted by ``backend.app`` via ``_safe_include`` under
``/api/v1/digital-twin``, following the same convention as the evolution /
architecture-graph / orchestrator modules.

Every endpoint wraps the deterministic ``DigitalTwinAPI`` facade (dispatch +
permissions + audit) and returns the backend standard envelope
``{"success": bool, "data": ...}``.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException

from modules.digital_twin.api import ApiResponse, DigitalTwinAPI
from modules.digital_twin.config.permissions import Permissions
from modules.digital_twin.core.digital_twin_manager import DigitalTwinManager
from modules.digital_twin.twin_engine import TwinEngine, TwinModelRegistry

router = APIRouter(tags=["digital-twin"])

# Single in-process engine instance: deterministic, so state is safe to
# share across requests. Created lazily on first use (mirrors the evolution
# engine router pattern).
_api: DigitalTwinAPI | None = None


def get_api() -> DigitalTwinAPI:
    global _api
    if _api is None:
        _api = DigitalTwinAPI(
            manager=DigitalTwinManager(),
            permissions=Permissions.for_role("admin"),
            twin_engine=TwinEngine(),
            twin_registry=TwinModelRegistry(),
        )
    return _api


def _ok(response: ApiResponse) -> dict[str, Any]:
    """Unwrap the facade ApiResponse into the backend envelope."""
    if not response.ok:
        status_code = response.status_code if response.status_code != 200 else 400
        raise HTTPException(status_code=status_code, detail=response.error)
    return {"success": True, "data": response.data}


@router.get("/status")
async def status() -> dict[str, Any]:
    return _ok(get_api().dispatch("status", role="admin"))


@router.get("/endpoints")
async def endpoints() -> dict[str, Any]:
    return _ok(get_api().dispatch("endpoints", role="admin"))


@router.get("/config")
async def config() -> dict[str, Any]:
    return _ok(get_api().dispatch("config", role="admin"))


@router.post("/start")
async def start() -> dict[str, Any]:
    return _ok(get_api().dispatch("start", role="admin"))


@router.post("/stop")
async def stop() -> dict[str, Any]:
    return _ok(get_api().dispatch("stop", role="admin"))


@router.post("/cycle")
async def cycle() -> dict[str, Any]:
    return _ok(get_api().dispatch("cycle", role="admin"))


@router.post("/tick")
async def tick(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return _ok(get_api().dispatch("tick", body, role="admin"))


@router.post("/build-twin")
async def build_twin(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return _ok(get_api().dispatch("build_twin", body, role="admin"))


@router.get("/snapshot")
async def snapshot(name: str) -> dict[str, Any]:
    return _ok(get_api().dispatch("snapshot", {"name": name}, role="admin"))


@router.post("/analyze")
async def analyze(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return _ok(get_api().dispatch("analyze", body, role="admin"))


@router.post("/validate")
async def validate(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return _ok(get_api().dispatch("validate", body, role="admin"))


# register_component is intentionally not exposed over REST: it registers an
# in-process callable component and cannot be serialized from a request body.
# It remains available through the DigitalTwinAPI facade for in-process callers.
