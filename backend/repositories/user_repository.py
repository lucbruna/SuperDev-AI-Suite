from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.user import User
from backend.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> User | None:
        """Find a user by email address (case-insensitive)."""
        query = select(self.model).where(func.lower(self.model.email) == email.lower())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Find a user by username (case-insensitive)."""
        query = select(self.model).where(func.lower(self.model.username) == username.lower())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def search(
        self,
        query_str: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        """Search users by email, username, or full name."""
        pattern = f"%{query_str}%"
        query = select(self.model).where(
            (self.model.email.ilike(pattern))
            | (self.model.username.ilike(pattern))
            | (self.model.full_name.ilike(pattern))
        )
        count_query = (
            select(func.count())
            .select_from(self.model)
            .where(
                (self.model.email.ilike(pattern))
                | (self.model.username.ilike(pattern))
                | (self.model.full_name.ilike(pattern))
            )
        )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_active_users(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        """List active users."""
        return await self.list(page=page, page_size=page_size, filters={"is_active": True})

    async def get_superusers(self) -> list[User]:
        """List all superuser accounts."""
        query = select(self.model).where(self.model.is_superuser)
        result = await self.db.execute(query)
        return list(result.scalars().all())
