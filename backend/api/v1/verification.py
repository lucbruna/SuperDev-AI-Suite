from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.verification.verification_loop import VerificationLoop

router = APIRouter()


class VerificationRequest(BaseModel):
    task_description: str
    language: str = "python"
    context: str | None = None
    requirements: list[str] = []
    existing_code: str | None = None
    test_files: dict[str, str] | None = None
    max_iterations: int = 3
    provider: str | None = None


class VerificationResponse(BaseModel):
    task_id: UUID
    success: bool
    stage: str
    final_code: str | None = None
    error: str | None = None
    iterations: int
    generation: dict | None = None
    execution: dict | None = None
    testing: dict | None = None
    review: dict | None = None
    correction: dict | None = None
    completed_at: str | None = None


@router.post("/verify", response_model=VerificationResponse, status_code=status.HTTP_201_CREATED)
async def run_verification(
    request: VerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> VerificationResponse:
    loop = VerificationLoop(
        provider_name=request.provider,
        max_iterations=request.max_iterations,
    )
    
    result = await loop.run(
        task_description=request.task_description,
        language=request.language,
        context=request.context,
        requirements=request.requirements,
        existing_code=request.existing_code,
        test_files=request.test_files,
    )
    
    return VerificationResponse(
        task_id=result.task_id,
        success=result.success,
        stage=result.stage.value,
        final_code=result.final_code,
        error=result.error,
        iterations=result.iterations,
        generation=result.generation.__dict__ if result.generation else None,
        execution=result.execution.__dict__ if result.execution else None,
        testing=result.testing.__dict__ if result.testing else None,
        review=result.review.__dict__ if result.review else None,
        correction=result.correction.__dict__ if result.correction else None,
        completed_at=result.completed_at.isoformat() if result.completed_at else None,
    )


class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str = "python"
    context: str | None = None
    provider: str | None = None


class CodeGenerationResponse(BaseModel):
    success: bool
    code: str
    explanation: str
    error: str | None = None


@router.post("/generate", response_model=CodeGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_code(
    request: CodeGenerationRequest,
    db: AsyncSession = Depends(get_db),
) -> CodeGenerationResponse:
    loop = VerificationLoop(provider_name=request.provider)
    result = await loop.generator.generate(
        task_description=request.prompt,
        language=request.language,
        context=request.context,
    )
    
    return CodeGenerationResponse(
        success=result.success,
        code=result.code,
        explanation=result.explanation,
        error=result.error,
    )


class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"


class CodeExecutionResponse(BaseModel):
    success: bool
    output: str
    error: str | None = None
    exit_code: int
    execution_time: float


@router.post("/execute", response_model=CodeExecutionResponse, status_code=status.HTTP_201_CREATED)
async def execute_code(
    request: CodeExecutionRequest,
    db: AsyncSession = Depends(get_db),
) -> CodeExecutionResponse:
    from backend.verification.executor import CodeExecutor
    
    executor = CodeExecutor()
    result = await executor.execute(request.code, request.language)
    
    return CodeExecutionResponse(
        success=result.success,
        output=result.stdout,
        error=result.stderr or result.error,
        exit_code=result.exit_code,
        execution_time=result.execution_time,
    )


class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"
    context: str | None = None
    provider: str | None = None


class CodeReviewResponse(BaseModel):
    success: bool
    score: int
    issues: list[dict[str, Any]] = []
    suggestions: list[str] = []
    security_issues: list[dict[str, Any]] = []
    performance_issues: list[dict[str, Any]] = []
    style_issues: list[dict[str, Any]] = []
    error: str | None = None


@router.post("/review", response_model=CodeReviewResponse, status_code=status.HTTP_201_CREATED)
async def review_code(
    request: CodeReviewRequest,
    db: AsyncSession = Depends(get_db),
) -> CodeReviewResponse:
    from ai_platform.providers.provider_registry import ProviderRegistry

    from backend.verification.reviewer import CodeReviewer
    
    registry = ProviderRegistry()
    provider = None
    if request.provider:
        provider_class = registry.get(request.provider)
        if provider_class:
            provider = provider_class()
    
    reviewer = CodeReviewer(provider)
    result = await reviewer.review(request.code, request.language, request.context)
    
    return CodeReviewResponse(
        success=result.success,
        score=result.score,
        issues=result.issues,
        suggestions=result.suggestions,
        security_issues=result.security_issues,
        performance_issues=result.performance_issues,
        style_issues=result.style_issues,
        error=result.error,
    )