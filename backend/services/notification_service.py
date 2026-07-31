from __future__ import annotations

from backend.database.models.notification import Notification
from backend.exceptions import AppException
from backend.repositories.notification_repository import NotificationRepository
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationService:
    """Service layer for Notification business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = NotificationRepository(db)

    async def get_notification(self, notification_id: str) -> Notification:
        """Get a notification by ID."""
        notification = await self.repository.get_by_id(notification_id)
        if not notification:
            raise AppException(message="Notification not found", code="NOTIFICATION_NOT_FOUND", status_code=404)
        return notification

    async def create_notification(
        self,
        organization_id: str,
        user_id: str,
        type: str,
        title: str,
        message: str,
        data: dict | None = None,
    ) -> Notification:
        """Create a new notification."""
        return await self.repository.create(
            organization_id=organization_id,
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            data=data or {},
        )

    async def list_notifications(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Notification], int]:
        """List notifications for a user."""
        return await self.repository.get_by_user(user_id, page, page_size)

    async def get_unread_count(self, user_id: str) -> int:
        """Count unread notifications for a user."""
        return await self.repository.get_unread_count(user_id)

    async def mark_read(self, notification_ids: list[str]) -> int:
        """Mark specific notifications as read."""
        return await self.repository.mark_read(notification_ids)

    async def mark_all_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        return await self.repository.mark_all_read(user_id)

    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification."""
        return await self.repository.delete(notification_id)
