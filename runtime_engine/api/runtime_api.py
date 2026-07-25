from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from runtime_engine.core.runtime_kernel import RuntimeKernel
from runtime_engine.runtime.runtime_context import RuntimeContext
from runtime_engine.runtime.runtime_executor import RuntimeExecutor

router = APIRouter(prefix="/api/v1/runtime", tags=["runtime"])

kernel: RuntimeKernel | None = None


def _get_kernel() -> RuntimeKernel:
    if kernel is None:
        raise RuntimeError("Kernel not initialized")
    return kernel


class ExecuteRequest(BaseModel):
    code: str
    language: str = Field(default="python")
    timeout: int = Field(default=30, ge=1, le=300)
    env_vars: dict[str, str] = Field(default_factory=dict)


class ExecuteResponse(BaseModel):
    session_id: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    error: str | None = None


@router.post("/execute", response_model=ExecuteResponse)
async def execute_code(req: ExecuteRequest) -> ExecuteResponse:
    k = _get_kernel()
    session_id = await k.session_manager.create_session(k.config)
    context = RuntimeContext(
        session_id=session_id,
        language=req.language,
        timeout=req.timeout,
        env_vars=req.env_vars,
    )
    executor = RuntimeExecutor(k.registry, k.config)
    result = await executor.execute(context, req.code)
    session = k.session_manager.get(session_id)
    if session:
        if result.error:
            session.fail()
        else:
            session.complete()
    return ExecuteResponse(
        session_id=session_id,
        exit_code=result.exit_code,
        stdout=result.stdout,
        stderr=result.stderr,
        duration=result.duration,
        error=result.error,
    )


@router.get("/sessions")
async def list_sessions() -> list[dict]:
    k = _get_kernel()
    return [s.model_dump() for s in k.session_manager.list_all()]


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> dict:
    k = _get_kernel()
    session = k.session_manager.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.model_dump()


@router.delete("/sessions/{session_id}")
async def destroy_session(session_id: str) -> dict:
    k = _get_kernel()
    session = k.session_manager.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    session.cancel()
    k.session_manager.remove(session_id)
    return {"status": "cancelled", "session_id": session_id}


@router.get("/sessions/{session_id}/logs")
async def get_session_logs(session_id: str, limit: int = 100, offset: int = 0) -> list[dict]:
    k = _get_kernel()
    logs = await k.logs.get_logs(session_id, limit=limit, offset=offset)
    return [entry.model_dump() for entry in logs]


@router.get("/health")
async def health() -> dict:
    k = _get_kernel()
    return await k.health()


@router.get("/languages")
async def languages() -> list[str]:
    k = _get_kernel()
    return k.registry.list()
