from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.notification import Notification
from backend.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Notification)

    async def get_by_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Notification], int]:
        """List notifications for a specific user, newest first."""
        base_query = select(self.model).where(self.model.user_id == user_id)
        count_query = select(func.count()).select_from(self.model).where(self.model.user_id == user_id)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = base_query.order_by(self.model.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_unread_count(self, user_id: str) -> int:
        """Count unread notifications for a user."""
        query = select(func.count()).select_from(self.model).where(
            self.model.user_id == user_id,
            not self.model.is_read,
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def mark_read(self, notification_ids: list[str]) -> int:
        """Mark specific notifications as read. Returns count of updated rows."""
        from sqlalchemy import update

        stmt = (
            update(self.model)
            .where(
                self.model.id.in_(notification_ids),
                not self.model.is_read,
            )
            .values(is_read=True, read_at=datetime.now(UTC))
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def mark_all_read(self, user_id: str) -> int:
        """Mark all unread notifications as read for a user. Returns count."""
        from sqlalchemy import update

        stmt = (
            update(self.model)
            .where(
                self.model.user_id == user_id,
                not self.model.is_read,
            )
            .values(is_read=True, read_at=datetime.now(UTC))
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def get_by_type(
        self,
        user_id: str,
        notification_type: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Notification], int]:
        """List notifications of a specific type for a user."""
        filters = {"user_id": user_id, "type": notification_type}
        return await self.list(page=page, page_size=page_size, filters=filters)
