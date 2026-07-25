from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from workflow_engine.core.engine import WorkflowEngine

router = APIRouter(prefix="/workflows", tags=["workflows"])


def _get_engine() -> WorkflowEngine:
    from workflow_engine.core.bootstrap import Bootstrap
    return Bootstrap.initialize()


@router.post("")
async def create_workflow(config: dict[str, Any]) -> dict[str, str]:
    engine = _get_engine()
    workflow_id = await engine.create_workflow(config)
    return {"workflow_id": workflow_id}


@router.get("")
async def list_workflows() -> dict[str, list[str]]:
    return {"workflow_ids": []}


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str) -> dict[str, Any]:
    engine = _get_engine()
    status = await engine.get_status(workflow_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"workflow_id": workflow_id, "status": status}


@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, context: dict[str, Any] = None) -> dict[str, Any]:
    if context is None:
        context = {}
    engine = _get_engine()
    try:
        result = await engine.execute(workflow_id, context)
        return {"workflow_id": workflow_id, "success": result.success, "output": result.output, "duration": result.duration}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/pause")
async def pause_workflow(workflow_id: str) -> dict[str, str]:
    engine = _get_engine()
    try:
        await engine.pause(workflow_id)
        return {"workflow_id": workflow_id, "status": "paused"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/resume")
async def resume_workflow(workflow_id: str) -> dict[str, str]:
    engine = _get_engine()
    try:
        await engine.resume(workflow_id)
        return {"workflow_id": workflow_id, "status": "resumed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str) -> dict[str, str]:
    engine = _get_engine()
    try:
        await engine.cancel(workflow_id)
        return {"workflow_id": workflow_id, "status": "cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{workflow_id}/status")
async def get_workflow_status(workflow_id: str) -> dict[str, Any]:
    engine = _get_engine()
    status = await engine.get_status(workflow_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"workflow_id": workflow_id, "status": status}
