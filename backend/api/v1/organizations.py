"""Organizations endpoint for the admin dashboard.

Backed by the canonical ``OrganizationService`` (``backend.services``),
which uses the shared ``database.models.organization`` models. Response
shapes match the admin dashboard contract.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.services.organization_service import OrganizationService

logger = logging.getLogger("superdev.api.organizations")

router = APIRouter(
    tags=["organizations"],
    dependencies=[Depends(get_current_active_user)],
)


def _serialize_org(org: Any, member_count: int | None = None) -> dict[str, Any]:
    return {
        "id": str(org.id),
        "name": org.name,
        "slug": org.slug,
        "description": org.description,
        "plan": getattr(org, "plan", "free"),
        "settings": getattr(org, "settings", None),
        "memberCount": member_count,
        "createdAt": org.created_at.isoformat() if org.created_at else None,
        "updatedAt": org.updated_at.isoformat() if org.updated_at else None,
    }


async def _member_count(service: OrganizationService, org_id: str) -> int:
    try:
        return await service.count_members(org_id)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("member count failed: %s", exc)
        return 0


@router.get("")
async def list_organizations(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List organizations (paginated)."""
    service = OrganizationService(db)
    orgs, total = await service.list_organizations(page=page, page_size=limit)
    items = []
    for org in orgs:
        items.append(_serialize_org(org, await _member_count(service, str(org.id))))
    return {
        "success": True,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 1,
        },
    }


@router.get("/my")
async def my_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Organizations the current user belongs to."""
    service = OrganizationService(db)
    orgs = await service.get_user_organizations(str(current_user.get("id", "")))
    items = [_serialize_org(org, await _member_count(service, str(org.id))) for org in orgs]
    return {"success": True, "data": {"items": items, "total": len(items)}}


@router.get("/{org_id}")
async def get_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get a single organization."""
    service = OrganizationService(db)
    try:
        org = await service.get_organization(org_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, "data": _serialize_org(org, await _member_count(service, org_id))}


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str | None = None
    plan: str = "free"


@router.post("", status_code=201)
async def create_organization(
    payload: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Create an organization (current user becomes owner/member)."""
    service = OrganizationService(db)
    try:
        org = await service.create_organization(
            name=payload.name,
            slug=payload.slug,
            description=payload.description,
            plan=payload.plan,
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    # Bind current user as the org owner
    try:
        from backend.database.models.organization import OrganizationMember

        membership = OrganizationMember(
            organization_id=str(org.id),
            user_id=str(current_user.get("id", "")),
            role="owner",
            invited_by=str(current_user.get("id", "")),
        )
        db.add(membership)
        await db.commit()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("owner membership bind failed: %s", exc)
        await db.rollback()

    return {"success": True, "data": _serialize_org(org, 1)}


class OrganizationUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    plan: str | None = None


@router.patch("/{org_id}")
async def update_organization(
    org_id: str,
    payload: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update organization fields."""
    service = OrganizationService(db)
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    try:
        org = await service.update_organization(org_id, **updates)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, "data": _serialize_org(org, await _member_count(service, org_id))}


@router.delete("/{org_id}", status_code=204)
async def delete_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an organization."""
    service = OrganizationService(db)
    try:
        await service.delete_organization(org_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return None


@router.get("/{org_id}/members")
async def list_members(
    org_id: str,
    page: int = 1,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List members of an organization (with user info when available)."""
    service = OrganizationService(db)
    members, total = await service.list_members(org_id, page=page, page_size=limit)

    # Enrich with user emails/names when the users table is reachable
    user_ids = [str(m.user_id) for m in members]
    users: dict[str, dict[str, Any]] = {}
    try:
        from sqlalchemy import select

        from backend.database.models.user import User

        result = await db.execute(select(User).where(User.id.in_(user_ids)))
        for u in result.scalars().all():
            users[str(u.id)] = {"email": u.email, "full_name": getattr(u, "full_name", None)}
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("member user enrichment failed: %s", exc)

    items = [
        {
            "id": str(m.id),
            "user_id": str(m.user_id),
            "organization_id": str(m.organization_id),
            "role": m.role,
            "joinedAt": m.joined_at.isoformat() if m.joined_at else None,
            "user": users.get(str(m.user_id), {"email": None, "full_name": None}),
        }
        for m in members
    ]
    return {
        "success": True,
        "data": {"items": items, "total": total, "page": page, "limit": limit},
    }
