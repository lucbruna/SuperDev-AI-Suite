from datetime import datetime
from typing import Any

import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.rbac import Action, Resource, require_permission
from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.utils.uuid_utils import generate_uuid

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    settings: dict | None = None
    visibility: str | None = None
    repository_url: str | None = None
    repository_branch: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    visibility: str = "private"
    settings: dict = {}
    repository_url: str | None = None
    repository_branch: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectList(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(require_permission(Resource.PROJECTS, Action.CREATE)),
) -> ProjectResponse:
    pid = generate_uuid()
    slug_base = re.sub(r"[^a-z0-9]+", "-", data.name.lower()).strip("-")[:40] or "project"

    # Resolve the user's organization (via membership), fallback to any org
    org_result = await db.execute(
        sa_text("SELECT organization_id FROM organization_members WHERE user_id = :uid LIMIT 1"),
        {"uid": str(user.id)},
    )
    org_row = org_result.fetchone()
    if org_row is None:
        org_result = await db.execute(sa_text("SELECT id FROM organizations LIMIT 1"))
        org_row = org_result.fetchone()
    if org_row is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No organization available to create a project",
        )
    organization_id = str(org_row[0])

    await db.execute(
        sa_text("""INSERT INTO projects (id, organization_id, owner_id, name, slug, description)
                    VALUES (:id, :organization_id, :owner_id, :name, :slug, :desc)"""),
        {
            "id": pid,
            "organization_id": organization_id,
            "owner_id": str(user.id),
            "name": data.name,
            "slug": f"{slug_base}-{pid[:8]}",
            "desc": data.description,
        },
    )
    await db.commit()
    result = await db.execute(
        sa_text("SELECT id, name, description, visibility, created_at, updated_at FROM projects WHERE id = :id"),
        {"id": pid},
    )
    row = result.fetchone()
    return ProjectResponse(
        id=str(row[0]), name=row[1], description=row[2], visibility=row[3], created_at=row[4], updated_at=row[5]
    )


@router.get("", response_model=ProjectList)
async def list_projects(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> ProjectList:
    offset = (page - 1) * page_size
    result = await db.execute(
        sa_text(
            "SELECT id, name, description, visibility, created_at, updated_at FROM projects ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        ),
        {"limit": page_size, "offset": offset},
    )
    rows = result.fetchall()
    total_result = await db.execute(sa_text("SELECT COUNT(*) FROM projects"))
    total = total_result.scalar() or 0
    pages = max(1, (total + page_size - 1) // page_size)

    return ProjectList(
        items=[
            ProjectResponse(id=str(r[0]), name=r[1], description=r[2], visibility=r[3], created_at=r[4], updated_at=r[5])
            for r in rows
        ],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    result = await db.execute(
        sa_text("SELECT id, name, description, visibility, created_at, updated_at FROM projects WHERE id = :id"),
        {"id": project_id},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponse(
        id=str(row[0]), name=row[1], description=row[2], visibility=row[3], created_at=row[4], updated_at=row[5]
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.PROJECTS, Action.UPDATE)),
) -> ProjectResponse:
    updates = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        return await get_project(project_id, db)

    # Handle settings as a full JSONB replace (frontend sends complete object)
    if "settings" in updates:
        import json
        updates["settings"] = json.dumps(updates["settings"])

    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = project_id
    await db.execute(
        sa_text(f"UPDATE projects SET {set_clause} WHERE id = :id"),
        updates,
    )
    await db.commit()
    return await get_project(project_id, db)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.PROJECTS, Action.DELETE)),
) -> None:
    result = await db.execute(sa_text("DELETE FROM projects WHERE id = :id"), {"id": project_id})
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
