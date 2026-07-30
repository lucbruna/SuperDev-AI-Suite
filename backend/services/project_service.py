from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.project import Project
from backend.exceptions import ProjectAlreadyExistsException, ProjectNotFoundException
from backend.repositories.project_repository import ProjectRepository


class ProjectService:
    """Service layer for Project business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = ProjectRepository(db)

    async def get_project(self, project_id: str) -> Project:
        """Get a project by ID."""
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException()
        return project

    async def get_project_by_slug(self, slug: str) -> Project:
        """Get a project by slug."""
        project = await self.repository.get_by_slug(slug)
        if not project:
            raise ProjectNotFoundException()
        return project

    async def create_project(
        self,
        organization_id: str,
        owner_id: str,
        name: str,
        slug: str,
        **kwargs: Any,
    ) -> Project:
        """Create a new project."""
        if await self.repository.slug_exists(slug):
            raise ProjectAlreadyExistsException()
        return await self.repository.create(
            organization_id=organization_id,
            owner_id=owner_id,
            name=name,
            slug=slug,
            **kwargs,
        )

    async def update_project(self, project_id: str, **kwargs: Any) -> Project:
        """Update project fields."""
        await self.get_project(project_id)  # Verify exists

        # Check slug uniqueness if changing
        if "slug" in kwargs:
            if await self.repository.slug_exists(kwargs["slug"], exclude_id=project_id):
                raise ProjectAlreadyExistsException()

        updated = await self.repository.update(project_id, **kwargs)
        if not updated:
            raise ProjectNotFoundException()
        return updated

    async def list_projects(
        self,
        organization_id: str | None = None,
        owner_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Project], int]:
        """List projects, optionally filtered by org or owner."""
        if organization_id:
            return await self.repository.get_by_organization(organization_id, page, page_size)
        if owner_id:
            return await self.repository.get_by_owner(owner_id, page, page_size)
        return await self.repository.list(page=page, page_size=page_size)

    async def search_projects(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Project], int]:
        """Search projects by name or description."""
        return await self.repository.search(query, page=page, page_size=page_size)

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        await self.get_project(project_id)  # Verify exists
        return await self.repository.delete(project_id)
