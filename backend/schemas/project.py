from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.base import BaseSchema


class ProjectBase(BaseSchema):
    """Base project fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-safe slug")
    description: str | None = Field(None, description="Project description")
    visibility: str = Field("private", description="Project visibility: private, team, public")
    settings: dict = Field(default_factory=dict, description="Project settings JSON")
    repository_url: str | None = Field(None, max_length=500, description="Git repository URL")
    repository_branch: str | None = Field(None, max_length=100, description="Default branch name")


class ProjectCreate(BaseModel):
    """Request to create a new project."""

    organization_id: str = Field(..., description="Organization UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-safe slug")
    description: str | None = Field(None, description="Project description")
    visibility: str = Field("private", description="Project visibility")
    settings: dict = Field(default_factory=dict, description="Project settings")
    repository_url: str | None = Field(None, description="Git repository URL")
    repository_branch: str | None = Field(None, description="Default branch name")


class ProjectUpdate(BaseModel):
    """Request to update project fields."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, description="Project description")
    visibility: str | None = Field(None, description="Project visibility")
    settings: dict | None = Field(None, description="Project settings")
    repository_url: str | None = Field(None, description="Git repository URL")
    repository_branch: str | None = Field(None, description="Default branch name")


class ProjectResponse(BaseSchema):
    """Full project response."""

    id: str = Field(..., description="Project UUID")
    organization_id: str = Field(..., description="Organization UUID")
    owner_id: str = Field(..., description="Owner user UUID")
    name: str = Field(..., description="Project name")
    slug: str = Field(..., description="URL-safe slug")
    description: str | None = Field(None, description="Project description")
    visibility: str = Field(..., description="Project visibility")
    settings: dict = Field(default_factory=dict, description="Project settings")
    repository_url: str | None = Field(None, description="Git repository URL")
    repository_branch: str | None = Field(None, description="Default branch name")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class ProjectMemberResponse(BaseSchema):
    """Project member response."""

    id: str = Field(..., description="Membership UUID")
    project_id: str = Field(..., description="Project UUID")
    user_id: str = Field(..., description="User UUID")
    role: str = Field(..., description="Member role: owner, admin, member, viewer")


class ProjectMemberCreate(BaseModel):
    """Request to add a member to a project."""

    user_id: str = Field(..., description="User UUID")
    role: str = Field("member", description="Member role: owner, admin, member, viewer")
