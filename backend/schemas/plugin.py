from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.base import BaseSchema


class PluginBase(BaseSchema):
    """Base plugin fields."""

    slug: str = Field(..., min_length=1, max_length=100, description="Plugin slug identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Plugin display name")
    version: str = Field(..., min_length=1, description="Semantic version string")
    description: str | None = Field(None, description="Plugin description")
    manifest: dict = Field(..., description="Plugin manifest JSON")
    config: dict = Field(default_factory=dict, description="Plugin configuration")


class PluginCreate(BaseModel):
    """Request to install a new plugin."""

    project_id: str = Field(..., description="Project UUID")
    slug: str = Field(..., min_length=1, max_length=100, description="Plugin slug")
    name: str = Field(..., min_length=1, max_length=255, description="Plugin name")
    version: str = Field(..., min_length=1, description="Plugin version")
    description: str | None = Field(None, description="Plugin description")
    manifest: dict = Field(..., description="Plugin manifest")
    config: dict = Field(default_factory=dict, description="Plugin configuration")


class PluginUpdate(BaseModel):
    """Request to update plugin fields."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Plugin name")
    description: str | None = Field(None, description="Plugin description")
    status: str | None = Field(None, description="Plugin status: installed, enabled, disabled, error")
    config: dict | None = Field(None, description="Plugin configuration")


class PluginResponse(BaseSchema):
    """Full plugin response."""

    id: str = Field(..., description="Plugin UUID")
    project_id: str = Field(..., description="Project UUID")
    slug: str = Field(..., description="Plugin slug")
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    description: str | None = Field(None, description="Plugin description")
    manifest: dict = Field(..., description="Plugin manifest")
    status: str = Field(..., description="Plugin status")
    config: dict = Field(default_factory=dict, description="Plugin configuration")
    installed_by: str = Field(..., description="Installer user UUID")
    created_at: datetime | None = Field(None, description="Installation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
