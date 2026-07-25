import uuid

from fastapi import APIRouter, Depends, Query, status

from ..auth.deps import get_current_user
from .schema import ProjectCreate, ProjectList, ProjectMemberResponse, ProjectResponse, ProjectUpdate
from .service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    return await service.create_project(data, owner_id=current_user["id"])


@router.get("/", response_model=ProjectList)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    organization_id: uuid.UUID | None = Query(None),
    owner_id: uuid.UUID | None = Query(None),
    search: str | None = Query(None),
    is_archived: bool | None = Query(None),
    service: ProjectService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    return await service.list_projects(
        page=page,
        page_size=page_size,
        organization_id=organization_id,
        owner_id=owner_id or current_user["id"],
        is_archived=is_archived,
        search=search,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    service: ProjectService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    return await service.get_project(project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    service: ProjectService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    return await service.update_project(project_id, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_project(
    project_id: uuid.UUID,
    service: ProjectService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    await service.archive_project(project_id)


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID = Query(...),
    role: str = Query("member"),
    service: ProjectService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    return await service.add_member(project_id, user_id, role)


@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
async def list_members(
    project_id: uuid.UUID,
    service: ProjectService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    members = await service.member_repo.get_members(project_id)
    return [await service._member_to_response(m) for m in members]


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    service: ProjectService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    await service.remove_member(project_id, user_id)


@router.put("/{project_id}/members/{user_id}", response_model=ProjectMemberResponse)
async def update_member_role(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str = Query(...),
    service: ProjectService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    return await service.update_member_role(project_id, user_id, role)