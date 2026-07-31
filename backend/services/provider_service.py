from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.provider import Provider
from backend.exceptions import ProviderNotFoundException, ProviderUnavailableException
from backend.repositories.provider_repository import ProviderRepository


class ProviderService:
    """Service layer for Provider business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = ProviderRepository(db)

    async def get_provider(self, provider_id: str) -> Provider:
        """Get a provider by ID."""
        provider = await self.repository.get_by_id(provider_id)
        if not provider:
            raise ProviderNotFoundException()
        return provider

    async def create_provider(
        self,
        project_id: str,
        created_by: str,
        name: str,
        type: str,
        config: dict,
        **kwargs: Any,
    ) -> Provider:
        """Create a new provider configuration."""
        valid_types = {"openai", "anthropic", "gemini", "ollama", "openrouter", "azure", "cohere"}
        if type not in valid_types:
            raise ProviderUnavailableException(provider=type)

        return await self.repository.create(
            project_id=project_id,
            created_by=created_by,
            name=name,
            type=type,
            config=config,
            **kwargs,
        )

    async def update_provider(self, provider_id: str, **kwargs: Any) -> Provider:
        """Update provider fields."""
        await self.get_provider(provider_id)
        updated = await self.repository.update(provider_id, **kwargs)
        if not updated:
            raise ProviderNotFoundException()
        return updated

    async def set_default(self, provider_id: str) -> Provider:
        """Set a provider as the default."""
        provider = await self.get_provider(provider_id)

        # Unset current defaults for same project
        defaults = await self.repository.get_defaults(provider.project_id)
        for default in defaults:
            if default.id != provider_id:
                await self.repository.update(default.id, is_default=False)

        return await self.update_provider(provider_id, is_default=True)

    async def list_providers(
        self,
        project_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Provider], int]:
        """List providers, optionally filtered by project."""
        if project_id:
            return await self.repository.get_by_project(project_id, page, page_size)
        return await self.repository.list(page=page, page_size=page_size)

    async def get_active_providers(self, project_id: str) -> list[Provider]:
        """Get all active providers for a project, ordered by priority."""
        return await self.repository.get_active_by_project(project_id)

    async def get_provider_by_type(self, project_id: str, provider_type: str) -> Provider:
        """Get the active provider of a specific type."""
        provider = await self.repository.get_active_by_type(project_id, provider_type)
        if not provider:
            raise ProviderNotFoundException()
        return provider

    async def delete_provider(self, provider_id: str) -> bool:
        """Delete a provider."""
        await self.get_provider(provider_id)
        return await self.repository.delete(provider_id)
