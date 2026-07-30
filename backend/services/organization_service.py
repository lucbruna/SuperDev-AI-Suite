from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.organization import Organization, OrganizationMember
from backend.exceptions import AppException
from backend.repositories.organization_repository import (
    OrganizationMemberRepository,
    OrganizationRepository,
)


class OrganizationService:
    """Service layer for Organization business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = OrganizationRepository(db)
        self.member_repository = OrganizationMemberRepository(db)

    async def get_organization(self, org_id: str) -> Organization:
        """Get an organization by ID."""
        org = await self.repository.get_by_id(org_id)
        if not org:
            raise AppException(
                message="Organization not found",
                code="ORGANIZATION_NOT_FOUND",
                status_code=404,
            )
        return org

    async def get_organization_by_slug(self, slug: str) -> Organization:
        """Get an organization by slug."""
        org = await self.repository.get_by_slug(slug)
        if not org:
            raise AppException(
                message="Organization not found",
                code="ORGANIZATION_NOT_FOUND",
                status_code=404,
            )
        return org

    async def create_organization(
        self,
        name: str,
        slug: str,
        **kwargs: Any,
    ) -> Organization:
        """Create a new organization."""
        if await self.repository.slug_exists(slug):
            raise AppException(
                message="Organization slug already taken",
                code="ORGANIZATION_SLUG_EXISTS",
                status_code=409,
            )
        return await self.repository.create(name=name, slug=slug, **kwargs)

    async def update_organization(self, org_id: str, **kwargs: Any) -> Organization:
        """Update organization fields."""
        await self.get_organization(org_id)
        if "slug" in kwargs and await self.repository.slug_exists(kwargs["slug"], exclude_id=org_id):
            raise AppException(
                message="Organization slug already taken",
                code="ORGANIZATION_SLUG_EXISTS",
                status_code=409,
            )
        updated = await self.repository.update(org_id, **kwargs)
        if not updated:
            raise AppException(
                message="Organization not found",
                code="ORGANIZATION_NOT_FOUND",
                status_code=404,
            )
        return updated

    async def list_organizations(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Organization], int]:
        """List all organizations."""
        return await self.repository.list(page=page, page_size=page_size)

    async def get_user_organizations(self, user_id: str) -> list[Organization]:
        """Get all organizations a user belongs to."""
        return await self.repository.get_by_user(user_id)

    async def delete_organization(self, org_id: str) -> bool:
        """Delete an organization."""
        await self.get_organization(org_id)
        return await self.repository.delete(org_id)

    # ── Member Management ────────────────────────────────────────

    async def add_member(
        self,
        org_id: str,
        user_id: str,
        role: str = "member",
        invited_by: str | None = None,
    ) -> OrganizationMember:
        """Add a member to an organization."""
        existing = await self.member_repository.get_membership(org_id, user_id)
        if existing:
            raise AppException(
                message="User is already a member",
                code="ALREADY_MEMBER",
                status_code=409,
            )
        return await self.member_repository.create(
            organization_id=org_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
        )

    async def remove_member(self, org_id: str, user_id: str) -> bool:
        """Remove a member from an organization."""
        return await self.member_repository.remove_member(org_id, user_id)

    async def list_members(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[OrganizationMember], int]:
        """List members of an organization."""
        return await self.member_repository.get_by_organization(org_id, page, page_size)

    async def get_membership(self, org_id: str, user_id: str) -> OrganizationMember | None:
        """Get a user's membership in an organization."""
        return await self.member_repository.get_membership(org_id, user_id)

    async def count_members(self, org_id: str) -> int:
        """Count members in an organization."""
        return await self.member_repository.count_members(org_id)

    async def update_member_role(self, org_id: str, user_id: str, role: str) -> OrganizationMember:
        """Update a member's role."""
        membership = await self.member_repository.get_membership(org_id, user_id)
        if not membership:
            raise AppException(
                message="Member not found",
                code="MEMBER_NOT_FOUND",
                status_code=404,
            )
        updated = await self.member_repository.update(membership.id, role=role)
        if not updated:
            raise AppException(
                message="Failed to update member role",
                code="MEMBER_UPDATE_FAILED",
                status_code=500,
            )
        return updated
