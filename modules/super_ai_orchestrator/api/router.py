"""FastAPI router exposing the Super AI Orchestrator through the API.

Mounted by ``backend.app`` via ``_safe_include`` under
``/api/v1/orchestrator``, following the same convention as the other
native modules.

Every endpoint wraps the deterministic ``OrchestratorAPI`` facade and
returns the backend's standard envelope ``{"success": bool, "data": ...}``.
Known failure modes map to HTTP errors: ``ValueError``/capacity → 400,
``KeyError`` (unknown task) → 404.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException

from modules.super_ai_orchestrator.api.orchestrator_api import OrchestratorAPI
from modules.super_ai_orchestrator.config import KernelConfig, OrchestratorConfig

router = APIRouter(tags=["orchestrator"])

# Single in-process orchestrator instance: deterministic, so state is safe
# to share across requests. Created lazily on first use.
_api: OrchestratorAPI | None = None


def get_api() -> OrchestratorAPI:
    global _api
    if _api is None:
        _api = OrchestratorAPI(
            OrchestratorConfig(),
            KernelConfig(),
        )
    return _api


def _ok(payload: dict[str, Any]) -> dict[str, Any]:
    """Wrap facade output into the backend envelope."""
    return {"success": True, "data": payload}


def _call(fn: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Run a facade call, mapping known exceptions to HTTP errors."""
    try:
        return _ok(fn(*args, **kwargs))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# --------------------------------------------------------------------- #
# Status & configuration
# --------------------------------------------------------------------- #
@router.get("/status")
async def status() -> dict[str, Any]:
    return _ok(get_api().status())


@router.get("/config")
async def config() -> dict[str, Any]:
    return _ok(get_api().config_dict())


@router.get("/governance")
async def governance() -> dict[str, Any]:
    return _ok(get_api().governance_policy())


# --------------------------------------------------------------------- #
# Tasks
# --------------------------------------------------------------------- #
@router.post("/tasks")
async def submit_task(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return _call(
        get_api().submit,
        kind=str(body.get("kind", "")),
        title=str(body.get("title", "")),
        payload=body.get("payload"),
        priority=body.get("priority"),
        owner_hint=body.get("owner_hint"),
        require_approval=body.get("require_approval"),
    )


@router.get("/tasks")
async def list_tasks(status: str | None = None) -> dict[str, Any]:
    return _call(get_api().tasks, status)


@router.get("/tasks/{seq}")
async def get_task(seq: int) -> dict[str, Any]:
    return _call(get_api().get, seq)


@router.post("/tasks/{seq}/approve")
async def approve_task(seq: int) -> dict[str, Any]:
    return _call(get_api().approve, seq)


@router.post("/tasks/{seq}/reject")
async def reject_task(seq: int, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return _call(get_api().reject, seq, str(body.get("reason", "rejected")))


@router.post("/tasks/{seq}/cancel")
async def cancel_task(seq: int) -> dict[str, Any]:
    return _call(get_api().cancel, seq)


@router.post("/tasks/{seq}/pause")
async def pause_task(seq: int) -> dict[str, Any]:
    return _call(get_api().pause, seq)


@router.post("/tasks/{seq}/resume")
async def resume_task(seq: int) -> dict[str, Any]:
    return _call(get_api().resume, seq)


@router.post("/tasks/{seq}/rollback")
async def rollback_task(seq: int) -> dict[str, Any]:
    return _call(get_api().rollback, seq)


# --------------------------------------------------------------------- #
# Scheduling
# --------------------------------------------------------------------- #
@router.post("/tick")
async def tick(body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    return _call(get_api().tick, body.get("slices"))


# --------------------------------------------------------------------- #
# Health, analytics, audit, events
# --------------------------------------------------------------------- #
@router.get("/health")
async def health() -> dict[str, Any]:
    return _ok(get_api().health())


@router.get("/metrics")
async def metrics() -> dict[str, Any]:
    return _ok(get_api().metrics())


@router.get("/analytics")
async def analytics() -> dict[str, Any]:
    return _ok(get_api().analytics_report())


@router.get("/audit")
async def audit() -> dict[str, Any]:
    return _ok(get_api().audit())


@router.get("/events")
async def events(event_type: str | None = None) -> dict[str, Any]:
    return _ok(get_api().events(event_type))


# --------------------------------------------------------------------- #
# Memory
# --------------------------------------------------------------------- #
@router.get("/memory")
async def memory_namespaces() -> dict[str, Any]:
    return _ok({"namespaces": get_api().memory_namespaces()})


@router.get("/memory/{namespace}")
async def memory_keys(namespace: str) -> dict[str, Any]:
    return _ok({"namespace": namespace, "keys": get_api().memory_keys(namespace)})


@router.post("/memory")
async def memory_remember(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return _call(
        get_api().memory_remember,
        str(body.get("namespace", "")),
        str(body.get("key", "")),
        body.get("value"),
    )


@router.get("/memory/{namespace}/{key}")
async def memory_recall(namespace: str, key: str) -> dict[str, Any]:
    return _ok(
        {
            "namespace": namespace,
            "key": key,
            "value": get_api().memory_recall(namespace, key),
        }
    )


@router.delete("/memory/{namespace}/{key}")
async def memory_forget(namespace: str, key: str) -> dict[str, Any]:
    return _ok(get_api().memory_forget(namespace, key))


# --------------------------------------------------------------------- #
# Integrations
# --------------------------------------------------------------------- #
@router.get("/integrations")
async def integrations() -> dict[str, Any]:
    return _ok(get_api().integrations())


@router.post("/integrations/{name}/invoke")
async def invoke_connector(
    name: str, body: dict[str, Any] = Body(default={})
) -> dict[str, Any]:
    action = str(body.pop("action", "invoke"))
    return _ok(get_api().invoke(name, action, **body))


# --------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------- #
@router.get("/dashboard")
async def dashboard() -> dict[str, Any]:
    return _ok(get_api().dashboard())
