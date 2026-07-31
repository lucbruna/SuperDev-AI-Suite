from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.base import BaseSchema


class AuditLogResponse(BaseSchema):
    """Audit log entry response."""

    id: str = Field(..., description="Audit log UUID")
    organization_id: str = Field(..., description="Organization UUID")
    user_id: str | None = Field(None, description="Acting user UUID (null for system actions)")
    action: str = Field(..., description="Action type: create, read, update, delete, login, logout, execute, deploy")
    resource_type: str = Field(..., description="Resource type (user, project, workflow, etc.)")
    resource_id: str | None = Field(None, description="Resource UUID")
    old_values: dict | None = Field(None, description="Previous field values for updates")
    new_values: dict | None = Field(None, description="New field values for creates/updates")
    ip_address: str | None = Field(None, max_length=45, description="Client IP address")
    user_agent: str | None = Field(None, description="Client user agent string")
    metadata: dict = Field(default_factory=dict, alias="extra_metadata", description="Additional metadata")
    created_at: datetime | None = Field(None, description="Event timestamp")

    model_config = {"from_attributes": True, "populate_by_name": True}


class AuditLogFilter(BaseModel):
    """Filters for querying audit logs."""

    action: str | None = Field(None, description="Filter by action type")
    resource_type: str | None = Field(None, description="Filter by resource type")
    user_id: str | None = Field(None, description="Filter by acting user")
    start_date: datetime | None = Field(None, description="Filter events after this date")
    end_date: datetime | None = Field(None, description="Filter events before this date")
