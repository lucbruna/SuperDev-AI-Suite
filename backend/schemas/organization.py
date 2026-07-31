from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.base import BaseSchema


class OrganizationCreate(BaseModel):
    """Request to create a new organization."""

    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-safe slug (unique)")
    description: str | None = Field(None, description="Organization description")
    plan: str = Field("free", description="Plan tier: free, pro, enterprise")


class OrganizationUpdate(BaseModel):
    """Request to update organization fields."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Organization name")
    description: str | None = Field(None, description="Organization description")
    plan: str | None = Field(None, description="Plan tier")
    settings: dict | None = Field(None, description="Organization settings")


class OrganizationResponse(BaseSchema):
    """Full organization response."""

    id: str = Field(..., description="Organization UUID")
    name: str = Field(..., description="Organization name")
    slug: str = Field(..., description="URL-safe slug")
    description: str | None = Field(None, description="Description")
    plan: str = Field(..., description="Plan tier")
    settings: dict = Field(default_factory=dict, description="Organization settings")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class OrganizationMemberResponse(BaseSchema):
    """Organization member response."""

    id: str = Field(..., description="Membership UUID")
    organization_id: str = Field(..., description="Organization UUID")
    user_id: str = Field(..., description="User UUID")
    role: str = Field(..., description="Member role: owner, admin, member, viewer")
    invited_at: datetime | None = Field(None, description="Invitation timestamp")
    joined_at: datetime | None = Field(None, description="Join timestamp")


class OrganizationMemberInvite(BaseModel):
    """Request to invite a user to an organization."""

    email: str = Field(..., description="Email address of the user to invite")
    role: str = Field("member", description="Role to assign: admin, member, viewer")
