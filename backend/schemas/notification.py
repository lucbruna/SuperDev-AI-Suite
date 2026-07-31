from __future__ import annotations

from datetime import datetime

from backend.schemas.base import BaseSchema
from pydantic import BaseModel, Field


class NotificationResponse(BaseSchema):
    """Notification response."""

    id: str = Field(..., description="Notification UUID")
    organization_id: str = Field(..., description="Organization UUID")
    user_id: str = Field(..., description="Recipient user UUID")
    type: str = Field(..., description="Notification type (info, warning, error, success)")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message body")
    data: dict = Field(default_factory=dict, description="Additional notification data")
    is_read: bool = Field(False, description="Whether the notification has been read")
    read_at: datetime | None = Field(None, description="Read timestamp")
    created_at: datetime | None = Field(None, description="Creation timestamp")


class NotificationMarkRead(BaseModel):
    """Request to mark notifications as read."""

    notification_ids: list[str] = Field(..., min_length=1, description="Notification UUIDs to mark as read")
