from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.runtime.base_runtime import Language, ResourceLimits, RuntimeConfig
from backend.runtime.runtime_manager import runtime_manager

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class ExecuteRequest(BaseModel):
    language: str
    code: str
    filename: str | None = None
    dependencies: list[str] = []
    env_vars: dict[str, str] = {}
    max_memory_mb: int = 512
    max_execution_time_seconds: int = 300
    stream: bool = False


class ExecuteResponse(BaseModel):
    run_id: str
    status: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    execution_time_ms: float = 0.0
    error: str | None = None


@router.post("/execute", response_model=ExecuteResponse)
async def execute_code(
    request: ExecuteRequest,
    db: AsyncSession = Depends(get_db),
) -> ExecuteResponse:
    from backend.dependencies import get_current_active_user
    user = await get_current_active_user(db=db)

    try:
        language = Language(request.language)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language: {request.language}",
        )

    run_id = generate_uuid()
    config = RuntimeConfig(
        language=language,
        code=request.code,
        filename=request.filename,
        dependencies=request.dependencies,
        env_vars=request.env_vars,
        resource_limits=ResourceLimits(
            max_memory_mb=request.max_memory_mb,
            max_execution_time_seconds=request.max_execution_time_seconds,
        ),
    )

    result = await runtime_manager.execute(config, run_id, user_id=str(user.id))

    return ExecuteResponse(
        run_id=result.run_id,
        status=result.status.value,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        execution_time_ms=result.execution_time_ms,
        error=result.error,
    )


@router.post("/stream")
async def stream_code(
    request: ExecuteRequest,
    db: AsyncSession = Depends(get_db),
):
    from backend.dependencies import get_current_active_user
    user = await get_current_active_user(db=db)

    try:
        language = Language(request.language)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language: {request.language}",
        )

    run_id = generate_uuid()
    config = RuntimeConfig(
        language=language,
        code=request.code,
        filename=request.filename,
        dependencies=request.dependencies,
        env_vars=request.env_vars,
        resource_limits=ResourceLimits(
            max_memory_mb=request.max_memory_mb,
            max_execution_time_seconds=request.max_execution_time_seconds,
        ),
    )

    async def generate():
        async for line in runtime_manager.stream(config, run_id, user_id=str(user.id)):
            yield line

    return StreamingResponse(generate(), media_type="text/plain")


@router.get("/languages")
async def list_languages() -> dict:
    return {
        "languages": [
            {"name": "python", "extensions": [".py"]},
            {"name": "nodejs", "extensions": [".js", ".ts", ".mjs"]},
            {"name": "shell", "extensions": [".sh", ".bash"]},
        ]
    }
