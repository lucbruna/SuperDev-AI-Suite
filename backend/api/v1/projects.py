from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import text as sa_text

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


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    is_public: bool = False
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
) -> ProjectResponse:
    pid = generate_uuid()
    await db.execute(
        sa_text("""INSERT INTO projects (id, name, description, owner_id)
                    VALUES (:id, :name, :desc, (SELECT id FROM users ORDER BY created_at LIMIT 1))"""),
        {"id": pid, "name": data.name, "desc": data.description},
    )
    await db.commit()
    result = await db.execute(sa_text("SELECT id, name, description, is_public, created_at, updated_at FROM projects WHERE id = :id"), {"id": pid})
    row = result.fetchone()
    return ProjectResponse(id=str(row[0]), name=row[1], description=row[2], is_public=row[3], created_at=row[4], updated_at=row[5])


@router.get("", response_model=ProjectList)
async def list_projects(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> ProjectList:
    offset = (page - 1) * page_size
    result = await db.execute(
        sa_text("SELECT id, name, description, is_public, created_at, updated_at FROM projects ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
        {"limit": page_size, "offset": offset},
    )
    rows = result.fetchall()
    total_result = await db.execute(sa_text("SELECT COUNT(*) FROM projects"))
    total = total_result.scalar() or 0
    pages = max(1, (total + page_size - 1) // page_size)

    return ProjectList(
        items=[ProjectResponse(id=str(r[0]), name=r[1], description=r[2], is_public=r[3], created_at=r[4], updated_at=r[5]) for r in rows],
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
        sa_text("SELECT id, name, description, is_public, created_at, updated_at FROM projects WHERE id = :id"),
        {"id": project_id},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponse(id=str(row[0]), name=row[1], description=row[2], is_public=row[3], created_at=row[4], updated_at=row[5])


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    updates = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        return await get_project(project_id, db)

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
) -> None:
    result = await db.execute(sa_text("DELETE FROM projects WHERE id = :id"), {"id": project_id})
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
