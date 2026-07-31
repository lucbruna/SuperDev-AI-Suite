from backend.database.session import get_db
from backend.middleware.authentication import get_current_user
from backend.organizations.schema import (
    InviteCreate,
    InviteResponse,
    OrganizationCreate,
    OrganizationList,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdate,
)
from backend.organizations.service import OrganizationService
from backend.users.model import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    service = OrganizationService(db)
    org = await service.create_organization(data, str(current_user.id))
    return OrganizationResponse.model_validate(org)


@router.get("", response_model=OrganizationList)
async def list_organizations(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> OrganizationList:
    service = OrganizationService(db)
    return await service.list_organizations(page=page, page_size=page_size)


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    service = OrganizationService(db)
    org = await service.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return OrganizationResponse.model_validate(org)


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    service = OrganizationService(db)
    org = await service.update_organization(org_id, data, str(current_user.id))
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return OrganizationResponse.model_validate(org)


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = OrganizationService(db)
    deleted = await service.delete_organization(org_id, str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return None


@router.post("/{org_id}/members", response_model=OrganizationMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    org_id: str,
    user_id: str,
    role: str = "member",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrganizationMemberResponse:
    service = OrganizationService(db)
    member = await service.add_member(org_id, user_id, role, str(current_user.id))
    return OrganizationMemberResponse.model_validate(member)


@router.get("/{org_id}/members", response_model=list[OrganizationMemberResponse])
async def list_members(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[OrganizationMemberResponse]:
    service = OrganizationService(db)
    return await service.get_members(org_id)


@router.delete("/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    org_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = OrganizationService(db)
    removed = await service.remove_member(org_id, user_id, str(current_user.id))
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return None


@router.put("/{org_id}/members/{user_id}", response_model=OrganizationMemberResponse)
async def update_member_role(
    org_id: str,
    user_id: str,
    role: str,
    db: AsyncSession = Depends(get_db),
) -> OrganizationMemberResponse:
    service = OrganizationService(db)
    member = await service.update_member_role(org_id, user_id, role)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return OrganizationMemberResponse.model_validate(member)


@router.post("/{org_id}/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    org_id: str,
    data: InviteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InviteResponse:
    service = OrganizationService(db)
    return await service.invite_member(org_id, data, str(current_user.id))
