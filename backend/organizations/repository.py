
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.organizations.model import Organization, OrganizationInvite, OrganizationMember
from backend.organizations.schema import OrganizationCreate, OrganizationUpdate


class OrganizationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, data: OrganizationCreate, owner_id: str) -> Organization:
        org = Organization(
            name=data.name,
            slug=data.slug,
            description=data.description,
            website=data.website,
            owner_id=owner_id,
        )
        self.db.add(org)
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def get_by_id(self, org_id: str) -> Organization | None:
        query = select(Organization).where(
            Organization.id == org_id,
            not Organization.is_deleted,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Organization | None:
        query = select(Organization).where(
            Organization.slug == slug,
            not Organization.is_deleted,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, org_id: str, data: OrganizationUpdate) -> Organization | None:
        org = await self.get_by_id(org_id)
        if not org:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(org, key, value)
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def delete(self, org_id: str) -> bool:
        org = await self.get_by_id(org_id)
        if not org:
            return False
        org.is_deleted = True
        org.deleted_at = func.now()
        await self.db.commit()
        return True

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict | None = None,
    ) -> tuple[list[Organization], int]:
        query = select(Organization).where(not Organization.is_deleted)
        count_query = select(func.count()).select_from(Organization).where(not Organization.is_deleted)

        if filters:
            for field, value in filters.items():
                if hasattr(Organization, field) and value is not None:
                    query = query.where(getattr(Organization, field) == value)
                    count_query = count_query.where(getattr(Organization, field) == value)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total


class OrganizationMemberRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, org_id: str, user_id: str, role: str) -> OrganizationMember:
        member = OrganizationMember(
            organization_id=org_id,
            user_id=user_id,
            role=role,
        )
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def remove(self, org_id: str, user_id: str) -> bool:
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id,
        )
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()
        if not member:
            return False
        await self.db.delete(member)
        await self.db.commit()
        return True

    async def update_role(self, org_id: str, user_id: str, role: str) -> OrganizationMember | None:
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id,
        )
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()
        if not member:
            return None
        member.role = role
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def list_by_org(self, org_id: str) -> list[OrganizationMember]:
        query = select(OrganizationMember).where(OrganizationMember.organization_id == org_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_by_user(self, user_id: str) -> list[OrganizationMember]:
        query = select(OrganizationMember).where(OrganizationMember.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class OrganizationInviteRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        org_id: str,
        email: str,
        role: str,
        invited_by: str,
    ) -> OrganizationInvite:
        invite = OrganizationInvite(
            organization_id=org_id,
            email=email,
            role=role,
            invited_by=invited_by,
        )
        self.db.add(invite)
        await self.db.commit()
        await self.db.refresh(invite)
        return invite

    async def get_by_token(self, token: str) -> OrganizationInvite | None:
        query = select(OrganizationInvite).where(
            OrganizationInvite.token == token,
            OrganizationInvite.status == "pending",
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, invite_id: str) -> OrganizationInvite | None:
        query = select(OrganizationInvite).where(OrganizationInvite.id == invite_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_status(self, invite_id: str, status: str) -> OrganizationInvite | None:
        invite = await self.get_by_id(invite_id)
        if not invite:
            return None
        invite.status = status
        await self.db.commit()
        await self.db.refresh(invite)
        return invite

    async def revoke_all_for_email(self, org_id: str, email: str) -> int:
        """Revoke all pending invites for an email in an organization."""
        query = select(OrganizationInvite).where(
            OrganizationInvite.organization_id == org_id,
            OrganizationInvite.email == email,
            OrganizationInvite.status == "pending",
        )
        result = await self.db.execute(query)
        invites = list(result.scalars().all())
        for invite in invites:
            invite.status = "revoked"
        if invites:
            await self.db.commit()
        return len(invites)
