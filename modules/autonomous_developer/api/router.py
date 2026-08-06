"""FastAPI router exposing the Autonomous Developer module through the API.

Mounted by ``backend.app`` via ``_safe_include`` under
``/api/v1/autonomous-developer``, following the same convention as the other
native modules.

Every endpoint wraps the ``DeveloperRuntime`` facade (phase orchestration
driven by registered planner/generator/validator/reviewer components) and
returns the backend standard envelope ``{"success": bool, "data": ...}``.
"""
from __future__ import annotations

import threading
from typing import Any

from fastapi import APIRouter, Body, HTTPException

from modules.autonomous_developer.core.runtime import DeveloperRuntime, build_runtime

router = APIRouter(tags=["autonomous-developer"])

# Single in-process runtime instance: deterministic, so state is safe to
# share across requests. Created lazily on first use.
_runtime: DeveloperRuntime | None = None

# Serializes /execute runs. Endpoints are plain ``def`` (FastAPI runs them in
# a threadpool) so the blocking runtime.execute() never stalls the event loop;
# the lock rejects overlapping runs against the shared singleton.
_exec_lock = threading.Lock()


def get_runtime() -> DeveloperRuntime:
    global _runtime
    if _runtime is None:
        _runtime = build_runtime()
    return _runtime


@router.get("/status")
def status() -> dict[str, Any]:
    return {"success": True, "data": get_runtime().status()}


@router.post("/execute")
def execute(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    goal = body.get("goal")
    if not goal or not isinstance(goal, str):
        raise HTTPException(status_code=400, detail="goal (string) is required")
    meta = body.get("meta")
    phases = body.get("phases")
    if phases is not None and not isinstance(phases, (list, tuple)):
        raise HTTPException(status_code=400, detail="phases must be a list of phase names")
    if not _exec_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409, detail="another execution is in progress"
        )
    try:
        runtime = get_runtime()
        context = runtime.execute(goal=goal, meta=meta, phases=phases)
    finally:
        _exec_lock.release()
    return {
        "success": True,
        "data": {
            "state": context.state.to_dict(),
            "stats": dict(context.stats),
            "session_id": context.stats.get("session_id"),
            "artifacts": list(context.artifacts),
        },
    }


@router.post("/reset")
def reset() -> dict[str, Any]:
    get_runtime().reset()
    return {"success": True, "data": {"reset": True}}


@router.get("/sessions")
def sessions(limit: int = 10) -> dict[str, Any]:
    runtime = get_runtime()
    return {
        "success": True,
        "data": {
            "active": [s.to_dict() for s in runtime.sessions.active()],
            "recent": [s.to_dict() for s in runtime.sessions.recent(limit=limit)],
        },
    }
