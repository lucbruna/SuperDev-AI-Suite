import math
import uuid
from datetime import datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from .model import Project, ProjectMember
from .repository import ProjectMemberRepository, ProjectRepository
from .schema import (
    OwnerInfo,
    ProjectCreate,
    ProjectList,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectUpdate,
)


class ProjectService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.repo = ProjectRepository(session)
        self.member_repo = ProjectMemberRepository(session)

    async def create_project(self, data: ProjectCreate, owner_id: uuid.UUID) -> ProjectResponse:
        existing = await self.repo.get_by_slug(data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Project with slug '{data.slug}' already exists",
            )
        project = await self.repo.create(data, owner_id)

        owner_member = ProjectMember(
            project_id=project.id,
            user_id=owner_id,
            role="owner",
        )
        await self.member_repo.add(owner_member)

        await self.session.commit()
        await self.session.refresh(project)
        return await self._to_response(project)

    async def get_project(self, project_id: uuid.UUID) -> ProjectResponse:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return await self._to_response(project)

    async def update_project(self, project_id: uuid.UUID, data: ProjectUpdate) -> ProjectResponse:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        if data.slug is not None and data.slug != project.slug:
            existing = await self.repo.get_by_slug(data.slug)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Project with slug '{data.slug}' already exists",
                )
        updated = await self.repo.update(project_id, data)
        await self.session.commit()
        await self.session.refresh(updated)
        return await self._to_response(updated)

    async def archive_project(self, project_id: uuid.UUID) -> ProjectResponse:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        project.is_archived = True
        project.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(project)
        return await self._to_response(project)

    async def delete_project(self, project_id: uuid.UUID) -> None:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        await self.repo.delete(project_id)
        await self.session.commit()

    async def list_projects(
        self,
        page: int = 1,
        page_size: int = 20,
        organization_id: uuid.UUID | None = None,
        owner_id: uuid.UUID | None = None,
        is_archived: bool | None = None,
        search: str | None = None,
    ) -> ProjectList:
        offset = (page - 1) * page_size
        projects, total = await self.repo.list(
            org_id=organization_id,
            user_id=owner_id,
            is_archived=is_archived,
            search=search,
            offset=offset,
            limit=page_size,
        )
        pages = math.ceil(total / page_size) if total > 0 else 1
        items = [await self._to_response(p) for p in projects]
        return ProjectList(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def add_member(
        self, project_id: uuid.UUID, user_id: uuid.UUID, role: str = "member"
    ) -> ProjectMemberResponse:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        existing = await self.member_repo.get_member(project_id, user_id)
        if existing:
            raise HTTPException(status_code=409, detail="User is already a member")
        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        created = await self.member_repo.add(member)
        await self.session.commit()
        return await self._member_to_response(created)

    async def remove_member(self, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        deleted = await self.member_repo.remove(project_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Member not found")
        await self.session.commit()

    async def update_member_role(self, project_id: uuid.UUID, user_id: uuid.UUID, role: str) -> ProjectMemberResponse:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        updated = await self.member_repo.update_role(project_id, user_id, role)
        if not updated:
            raise HTTPException(status_code=404, detail="Member not found")
        await self.session.commit()
        return await self._member_to_response(updated)

    async def _to_response(self, project: Project) -> ProjectResponse:
        members = await self.member_repo.get_members(project.id)
        owner_info = None
        if project.owner:
            owner_info = OwnerInfo(
                id=project.owner.id,
                email=getattr(project.owner, "email", None),
                display_name=getattr(project.owner, "display_name", None),
            )
        return ProjectResponse(
            id=project.id,
            name=project.name,
            slug=project.slug,
            description=project.description,
            owner_id=project.owner_id,
            owner=owner_info,
            organization_id=project.organization_id,
            workspace_id=project.workspace_id,
            language=project.language,
            framework=project.framework,
            template=project.template,
            is_archived=project.is_archived,
            is_public=project.is_public,
            settings=project.settings,
            tags=project.tags,
            member_count=len(members),
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    async def _member_to_response(self, member: ProjectMember) -> ProjectMemberResponse:
        user_info = None
        if member.user:
            user_info = OwnerInfo(
                id=member.user.id,
                email=getattr(member.user, "email", None),
                display_name=getattr(member.user, "display_name", None),
            )
        return ProjectMemberResponse(
            id=member.id,
            project_id=member.project_id,
            user_id=member.user_id,
            role=member.role,
            created_at=member.created_at,
            user=user_info,
        )
