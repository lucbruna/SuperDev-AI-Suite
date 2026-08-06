"""FastAPI router exposing the Self-Healing Engine through the API.

Mounted by ``backend.app`` via ``_safe_include`` under
``/api/v1/self-healing``, following the same convention as the other native
modules.

Every endpoint wraps the deterministic ``HealingEngine`` facade (one healing
cycle per ``run``) and returns the backend standard envelope
``{"success": bool, "data": ...}``.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from modules.self_healing_engine.core.healing_context import HealingContext
from modules.self_healing_engine.core.healing_engine import HealingEngine

router = APIRouter(tags=["self-healing"])

# Single in-process engine instance with a shared context (bus, state,
# memory). Deterministic, so sharing across requests is safe.
_engine: HealingEngine | None = None
_ctx: HealingContext | None = None


def get_engine() -> tuple[HealingEngine, HealingContext]:
    global _engine, _ctx
    if _engine is None:
        _ctx = HealingContext()
        _engine = HealingEngine()
    return _engine, _ctx


@router.get("/status")
async def status() -> dict[str, Any]:
    engine, ctx = get_engine()
    return {
        "success": True,
        "data": {
            "cycles": engine.cycles,
            "events": len(ctx.events.history()),
            "memory": len(ctx.memory),
            "artifacts": sorted(ctx.artifacts),
            "summary": ctx.summary(),
        },
    }


@router.post("/run")
async def run(body: dict[str, Any] | None = Body(default=None)) -> dict[str, Any]:
    engine, ctx = get_engine()
    incident = (body or {}).get("incident") if isinstance(body, dict) else None
    result = engine.run(ctx, incident)
    return {"success": True, "data": result.to_dict()}


@router.get("/events")
async def events() -> dict[str, Any]:
    _, ctx = get_engine()
    return {
        "success": True,
        "data": {
            "events": [event.to_dict() for event in ctx.events.history()],
            "last_sequence": ctx.events.last_sequence,
        },
    }
