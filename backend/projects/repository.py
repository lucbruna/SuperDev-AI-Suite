import uuid
from datetime import datetime

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import Project, ProjectMember
from .schema import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ProjectCreate, owner_id: uuid.UUID) -> Project:
        project = Project(
            name=data.name,
            description=data.description,
            slug=data.slug,
            organization_id=data.organization_id,
            owner_id=owner_id,
            template=data.template,
            language=data.language,
            framework=data.framework,
            is_public=data.is_public,
            tags=data.tags,
        )
        self.session.add(project)
        await self.session.flush()
        return project

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Project | None:
        stmt = select(Project).where(Project.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, project_id: uuid.UUID, data: ProjectUpdate) -> Project | None:
        project = await self.get_by_id(project_id)
        if not project:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        project.updated_at = datetime.utcnow()
        await self.session.flush()
        return project

    async def delete(self, project_id: uuid.UUID) -> bool:
        project = await self.get_by_id(project_id)
        if not project:
            return False
        await self.session.delete(project)
        await self.session.flush()
        return True

    def _apply_filters(
        self,
        stmt: Select,
        org_id: uuid.UUID | None,
        user_id: uuid.UUID | None,
        is_archived: bool | None,
        search: str | None,
    ) -> Select:
        conditions = []
        if org_id is not None:
            conditions.append(Project.organization_id == org_id)
        if user_id is not None:
            conditions.append(Project.owner_id == user_id)
        if is_archived is not None:
            conditions.append(Project.is_archived == is_archived)
        if search:
            pattern = f"%{search}%"
            conditions.append(or_(Project.name.ilike(pattern), Project.description.ilike(pattern)))
        if conditions:
            stmt = stmt.where(and_(*conditions))
        return stmt

    async def list(
        self,
        org_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        is_archived: bool | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Project], int]:
        base_stmt = select(Project)
        count_stmt = select(func.count(Project.id))

        base_stmt = self._apply_filters(base_stmt, org_id, user_id, is_archived, search)
        count_stmt = self._apply_filters(count_stmt, org_id, user_id, is_archived, search)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = base_stmt.order_by(Project.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        projects = list(result.scalars().all())

        return projects, total


class ProjectMemberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, member: ProjectMember) -> ProjectMember:
        self.session.add(member)
        await self.session.flush()
        return member

    async def remove(self, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()
        if not member:
            return False
        await self.session.delete(member)
        await self.session.flush()
        return True

    async def update_role(self, project_id: uuid.UUID, user_id: uuid.UUID, role: str) -> ProjectMember | None:
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()
        if not member:
            return None
        member.role = role
        await self.session.flush()
        return member

    async def get_members(self, project_id: uuid.UUID) -> list[ProjectMember]:
        stmt = (
            select(ProjectMember).where(ProjectMember.project_id == project_id).order_by(ProjectMember.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_member(self, project_id: uuid.UUID, user_id: uuid.UUID) -> ProjectMember | None:
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
