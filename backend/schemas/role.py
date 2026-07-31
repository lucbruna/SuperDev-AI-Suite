from __future__ import annotations

from datetime import datetime

from backend.schemas.base import BaseSchema
from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    """Request to create a new role."""

    name: str = Field(..., min_length=1, max_length=100, description="Role name (unique)")
    description: str | None = Field(None, description="Role description")
    organization_id: str | None = Field(None, description="Organization UUID (null for system roles)")
    permission_ids: list[str] = Field(default_factory=list, description="Permission UUIDs to assign")


class RoleResponse(BaseSchema):
    """Role response with permissions."""

    id: str = Field(..., description="Role UUID")
    name: str = Field(..., description="Role name")
    description: str | None = Field(None, description="Role description")
    is_system: bool = Field(False, description="Whether this is a system role")
    organization_id: str | None = Field(None, description="Organization UUID")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class PermissionResponse(BaseSchema):
    """Permission response."""

    id: str = Field(..., description="Permission UUID")
    name: str = Field(..., description="Permission name")
    description: str | None = Field(None, description="Permission description")
    resource: str = Field(..., description="Resource type this permission applies to")
    action: str = Field(..., description="Action type: read, write, delete, execute, admin")
    is_system: bool = Field(False, description="Whether this is a system permission")


class UserRoleAssign(BaseModel):
    """Request to assign a role to a user."""

    user_id: str = Field(..., description="User UUID")
    role_id: str = Field(..., description="Role UUID")
    organization_id: str | None = Field(None, description="Organization scope UUID")
    project_id: str | None = Field(None, description="Project scope UUID")
    expires_at: datetime | None = Field(None, description="Role assignment expiry")
