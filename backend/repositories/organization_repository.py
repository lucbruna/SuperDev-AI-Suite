from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.organization import Organization, OrganizationMember
from backend.repositories.base_repository import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for Organization entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Organization)

    async def get_by_slug(self, slug: str) -> Organization | None:
        """Find an organization by its URL slug."""
        query = select(self.model).where(self.model.slug == slug)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: str) -> list[Organization]:
        """Get all organizations a user belongs to."""
        query = (
            select(self.model)
            .join(OrganizationMember, OrganizationMember.organization_id == self.model.id)
            .where(OrganizationMember.user_id == user_id)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        query_str: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Organization], int]:
        """Search organizations by name or description."""
        pattern = f"%{query_str}%"
        where_clause = (self.model.name.ilike(pattern)) | (self.model.description.ilike(pattern))

        query = select(self.model).where(where_clause)
        count_query = select(func.count()).select_from(self.model).where(where_clause)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def slug_exists(self, slug: str, exclude_id: str | None = None) -> bool:
        """Check if an organization slug is already taken."""
        query = select(func.count()).select_from(self.model).where(self.model.slug == slug)
        if exclude_id:
            query = query.where(self.model.id != exclude_id)
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0

    async def get_by_plan(
        self,
        plan: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Organization], int]:
        """List organizations on a specific plan tier."""
        return await self.list(page=page, page_size=page_size, filters={"plan": plan})


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    """Repository for OrganizationMember entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, OrganizationMember)

    async def get_by_organization(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[OrganizationMember], int]:
        """List members of an organization."""
        return await self.list(page=page, page_size=page_size, filters={"organization_id": org_id})

    async def get_by_user(self, user_id: str) -> list[OrganizationMember]:
        """Get all organization memberships for a user."""
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_membership(self, org_id: str, user_id: str) -> OrganizationMember | None:
        """Get a specific user's membership in an organization."""
        query = select(self.model).where(
            self.model.organization_id == org_id,
            self.model.user_id == user_id,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def count_members(self, org_id: str) -> int:
        """Count members in an organization."""
        query = select(func.count()).select_from(self.model).where(self.model.organization_id == org_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_by_role(
        self,
        org_id: str,
        role: str,
    ) -> list[OrganizationMember]:
        """Get all members with a specific role in an organization."""
        query = select(self.model).where(
            self.model.organization_id == org_id,
            self.model.role == role,
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def remove_member(self, org_id: str, user_id: str) -> bool:
        """Remove a member from an organization. Returns True if removed."""
        instance = await self.get_membership(org_id, user_id)
        if not instance:
            return False
        await self.db.delete(instance)
        await self.db.commit()
        return True
