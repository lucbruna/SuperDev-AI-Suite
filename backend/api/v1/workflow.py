from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.rbac import Action, Resource, require_permission
from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.workflow_integration.service import WorkflowIntegrationService, get_workflow_integration_service
from backend.workflow.workflow_manager import workflow_manager

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class CreateWorkflowRequest(BaseModel):
    name: str
    description: str = ""
    steps: list[dict[str, Any]]
    variables: dict[str, Any] = {}
    tags: list[str] = []


class CreateWorkflowResponse(BaseModel):
    workflow_id: str
    name: str
    description: str
    steps: list[dict[str, Any]]
    tags: list[str]


class ExecuteWorkflowRequest(BaseModel):
    variables: dict[str, Any] = {}


class ExecuteWorkflowResponse(BaseModel):
    run_id: str
    workflow_id: str
    status: str
    result: dict[str, Any]


class VerificationWorkflowRequest(BaseModel):
    task_description: str
    language: str = "python"
    context: str | None = None
    requirements: list[str] = []
    existing_code: str | None = None
    test_files: dict[str, str] | None = None
    max_iterations: int = 3
    provider: str | None = None


class VerificationWorkflowResponse(BaseModel):
    success: bool
    stage: str
    final_code: str | None = None
    error: str | None = None
    iterations: int
    generation: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    testing: dict[str, Any] | None = None
    review: dict[str, Any] | None = None
    correction: dict[str, Any] | None = None


@router.post("", response_model=CreateWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    request: CreateWorkflowRequest,
    db: AsyncSession = Depends(get_db),
    service: WorkflowIntegrationService = Depends(get_workflow_integration_service),
    _user: Any = Depends(require_permission(Resource.WORKFLOWS, Action.CREATE)),
) -> CreateWorkflowResponse:
    definition = workflow_manager.create_definition(
        name=request.name,
        description=request.description,
        steps=request.steps,
        variables=request.variables,
        tags=request.tags,
    )

    return CreateWorkflowResponse(
        workflow_id=str(definition.id),
        name=definition.name,
        description=definition.description,
        steps=[s.to_dict() for s in definition.steps],
        tags=definition.tags,
    )


@router.get("", response_model=list[CreateWorkflowResponse])
async def list_workflows(
    tags: list[str] | None = None,
    db: AsyncSession = Depends(get_db),
    service: WorkflowIntegrationService = Depends(get_workflow_integration_service),
) -> list[CreateWorkflowResponse]:
    definitions = service.list_workflows(tags)

    return [
        CreateWorkflowResponse(
            workflow_id=str(d.id),
            name=d.name,
            description=d.description,
            steps=[s.to_dict() for s in d.steps],
            tags=d.tags,
        )
        for d in definitions
    ]


@router.get("/{workflow_id}", response_model=CreateWorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: WorkflowIntegrationService = Depends(get_workflow_integration_service),
) -> CreateWorkflowResponse:
    definition = service.workflow_manager.get_definition(str(workflow_id))
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    return CreateWorkflowResponse(
        workflow_id=str(definition.id),
        name=definition.name,
        description=definition.description,
        steps=[s.to_dict() for s in definition.steps],
        tags=definition.tags,
    )


@router.post("/{workflow_id}/execute", response_model=ExecuteWorkflowResponse)
async def execute_workflow(
    workflow_id: UUID,
    request: ExecuteWorkflowRequest = ExecuteWorkflowRequest(),
    db: AsyncSession = Depends(get_db),
    service: WorkflowIntegrationService = Depends(get_workflow_integration_service),
    _user: Any = Depends(require_permission(Resource.WORKFLOWS, Action.EXECUTE)),
) -> ExecuteWorkflowResponse:
    result = await service.execute_verification_workflow(
        workflow_id=str(workflow_id),
        variables=request.variables,
    )

    return ExecuteWorkflowResponse(
        run_id=str(result.get("run_id", "")),
        workflow_id=str(workflow_id),
        status=result.get("status", "failed"),
        result=result,
    )


@router.post("/verify", response_model=VerificationWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def run_verification(
    request: VerificationWorkflowRequest,
    db: AsyncSession = Depends(get_db),
    service: WorkflowIntegrationService = Depends(get_workflow_integration_service),
    _user: Any = Depends(require_permission(Resource.WORKFLOWS, Action.EXECUTE)),
) -> VerificationWorkflowResponse:
    result = await service.run_verification_workflow(
        task_description=request.task_description,
        language=request.language,
        context=request.context,
        requirements=request.requirements,
        existing_code=request.existing_code,
        test_files=request.test_files,
        max_iterations=request.max_iterations,
        provider_name=request.provider,
    )

    return VerificationWorkflowResponse(
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
    )


@router.post("/verify/workflow", response_model=CreateWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_verification_workflow(
    request: VerificationWorkflowRequest,
    db: AsyncSession = Depends(get_db),
    service: WorkflowIntegrationService = Depends(get_workflow_integration_service),
    _user: Any = Depends(require_permission(Resource.WORKFLOWS, Action.CREATE)),
) -> CreateWorkflowResponse:
    definition = await service.create_verification_workflow(
        name=f"Verify: {request.task_description[:50]}",
        task_description=request.task_description,
        language=request.language,
        context=request.context,
        requirements=request.requirements,
        existing_code=request.existing_code,
        test_files=request.test_files,
        max_iterations=request.max_iterations,
        provider_name=request.provider,
    )

    return CreateWorkflowResponse(
        workflow_id=str(definition.id),
        name=definition.name,
        description=definition.description,
        steps=[s.to_dict() for s in definition.steps],
        tags=definition.tags,
    )
