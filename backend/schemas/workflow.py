from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.base import BaseSchema


class WorkflowBase(BaseSchema):
    """Base workflow fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Workflow name")
    description: str | None = Field(None, description="Workflow description")
    definition: dict = Field(..., description="DAG workflow definition JSON")
    tags: list[str] = Field(default_factory=list, description="Workflow tags")
    is_template: bool = Field(False, description="Whether this is a template workflow")


class WorkflowCreate(BaseModel):
    """Request to create a new workflow."""

    project_id: str = Field(..., description="Project UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Workflow name")
    description: str | None = Field(None, description="Workflow description")
    definition: dict = Field(..., description="DAG workflow definition JSON")
    tags: list[str] = Field(default_factory=list, description="Workflow tags")
    is_template: bool = Field(False, description="Whether this is a template")


class WorkflowUpdate(BaseModel):
    """Request to update workflow fields."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Workflow name")
    description: str | None = Field(None, description="Workflow description")
    definition: dict | None = Field(None, description="Workflow definition JSON")
    tags: list[str] | None = Field(None, description="Workflow tags")


class WorkflowResponse(BaseSchema):
    """Full workflow response."""

    id: str = Field(..., description="Workflow UUID")
    project_id: str = Field(..., description="Project UUID")
    name: str = Field(..., description="Workflow name")
    description: str | None = Field(None, description="Workflow description")
    definition: dict = Field(..., description="DAG workflow definition")
    version: int = Field(1, description="Workflow version")
    tags: list[str] = Field(default_factory=list, description="Workflow tags")
    is_template: bool = Field(False, description="Whether this is a template")
    created_by: str = Field(..., description="Creator user UUID")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class WorkflowRunResponse(BaseSchema):
    """Workflow run response."""

    id: str = Field(..., description="Run UUID")
    workflow_id: str = Field(..., description="Workflow UUID")
    status: str = Field(..., description="Run status: pending, running, completed, failed, cancelled")
    trigger: str = Field(..., description="Run trigger type")
    triggered_by: str | None = Field(None, description="Triggering user UUID")
    variables: dict = Field(default_factory=dict, description="Run variables")
    result: dict | None = Field(None, description="Run result")
    error: str | None = Field(None, description="Error message if failed")
    started_at: datetime | None = Field(None, description="Run start timestamp")
    completed_at: datetime | None = Field(None, description="Run completion timestamp")
    created_at: datetime | None = Field(None, description="Record creation timestamp")


class WorkflowStepResponse(BaseSchema):
    """Workflow step execution response."""

    id: str = Field(..., description="Step UUID")
    run_id: str = Field(..., description="Run UUID")
    step_id: str = Field(..., description="Step identifier within workflow")
    name: str = Field(..., description="Step display name")
    step_type: str = Field(..., description="Step type")
    config: dict = Field(..., description="Step configuration")
    status: str = Field(..., description="Step status")
    input: dict | None = Field(None, description="Step input data")
    output: dict | None = Field(None, description="Step output data")
    error: str | None = Field(None, description="Error message if failed")
    retries: int = Field(0, description="Number of retries attempted")
    started_at: datetime | None = Field(None, description="Step start timestamp")
    completed_at: datetime | None = Field(None, description="Step completion timestamp")
    created_at: datetime | None = Field(None, description="Record creation timestamp")
