from sqlalchemy.ext.asyncio import AsyncSession

from backend.organizations.events import (
    MemberAdded,
    MemberRemoved,
    OrganizationCreated,
    OrganizationDeleted,
    OrganizationUpdated,
)
from backend.organizations.model import Organization
from backend.organizations.repository import (
    OrganizationMemberRepository,
    OrganizationRepository,
)
from backend.organizations.schema import (
    InviteCreate,
    OrganizationCreate,
    OrganizationList,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdate,
)


class OrganizationService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = OrganizationRepository(db)
        self.member_repository = OrganizationMemberRepository(db)

    async def create_organization(
        self,
        data: OrganizationCreate,
        owner_id: str,
    ) -> Organization:
        org = await self.repository.create(data, owner_id)
        await self.member_repository.add(org.id, owner_id, "owner")
        OrganizationCreated(org_id=org.id, actor_id=owner_id)
        return org

    async def get_organization(self, org_id: str) -> Organization | None:
        return await self.repository.get_by_id(org_id)

    async def get_organization_by_slug(self, slug: str) -> Organization | None:
        return await self.repository.get_by_slug(slug)

    async def update_organization(
        self,
        org_id: str,
        data: OrganizationUpdate,
        actor_id: str,
    ) -> Organization | None:
        org = await self.repository.update(org_id, data)
        if org:
            OrganizationUpdated(org_id=org_id, actor_id=actor_id)
        return org

    async def delete_organization(self, org_id: str, actor_id: str) -> bool:
        deleted = await self.repository.delete(org_id)
        if deleted:
            OrganizationDeleted(org_id=org_id, actor_id=actor_id)
        return deleted

    async def list_organizations(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict | None = None,
    ) -> OrganizationList:
        items, total = await self.repository.list(page=page, page_size=page_size, filters=filters)
        pages = max(1, (total + page_size - 1) // page_size)
        return OrganizationList(
            items=[OrganizationResponse.model_validate(o) for o in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )

    async def add_member(
        self,
        org_id: str,
        user_id: str,
        role: str,
        actor_id: str,
    ):
        member = await self.member_repository.add(org_id, user_id, role)
        MemberAdded(org_id=org_id, actor_id=actor_id, user_id=user_id)
        return member

    async def remove_member(self, org_id: str, user_id: str, actor_id: str) -> bool:
        removed = await self.member_repository.remove(org_id, user_id)
        if removed:
            MemberRemoved(org_id=org_id, actor_id=actor_id, user_id=user_id)
        return removed

    async def update_member_role(
        self,
        org_id: str,
        user_id: str,
        role: str,
    ):
        return await self.member_repository.update_role(org_id, user_id, role)

    async def get_members(self, org_id: str) -> list[OrganizationMemberResponse]:
        members = await self.member_repository.list_by_org(org_id)
        return [OrganizationMemberResponse.model_validate(m) for m in members]

    async def invite_member(self, org_id: str, data: InviteCreate, actor_id: str):
        pass

    async def accept_invite(self, token: str):
        pass
