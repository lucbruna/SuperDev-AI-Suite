from __future__ import annotations

from typing import Any

from backend.database.models.plugin import Plugin
from backend.exceptions import PluginNotFoundException, PluginValidationException
from backend.repositories.plugin_repository import PluginRepository
from sqlalchemy.ext.asyncio import AsyncSession


class PluginService:
    """Service layer for Plugin business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = PluginRepository(db)

    async def get_plugin(self, plugin_id: str) -> Plugin:
        """Get a plugin by ID."""
        plugin = await self.repository.get_by_id(plugin_id)
        if not plugin:
            raise PluginNotFoundException()
        return plugin

    async def get_plugin_by_slug(self, project_id: str, slug: str) -> Plugin:
        """Get a plugin by project and slug."""
        plugin = await self.repository.get_by_slug(project_id, slug)
        if not plugin:
            raise PluginNotFoundException()
        return plugin

    async def install_plugin(
        self,
        project_id: str,
        installed_by: str,
        slug: str,
        name: str,
        version: str,
        manifest: dict,
        **kwargs: Any,
    ) -> Plugin:
        """Install a new plugin."""
        if await self.repository.slug_exists(project_id, slug):
            raise PluginValidationException(detail=f"Plugin '{slug}' already installed")

        self._validate_manifest(manifest)
        return await self.repository.create(
            project_id=project_id,
            installed_by=installed_by,
            slug=slug,
            name=name,
            version=version,
            manifest=manifest,
            **kwargs,
        )

    async def update_plugin(self, plugin_id: str, **kwargs: Any) -> Plugin:
        """Update plugin fields."""
        await self.get_plugin(plugin_id)
        updated = await self.repository.update(plugin_id, **kwargs)
        if not updated:
            raise PluginNotFoundException()
        return updated

    async def enable_plugin(self, plugin_id: str) -> Plugin:
        """Enable a plugin."""
        return await self.update_plugin(plugin_id, status="enabled")

    async def disable_plugin(self, plugin_id: str) -> Plugin:
        """Disable a plugin."""
        return await self.update_plugin(plugin_id, status="disabled")

    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin."""
        await self.get_plugin(plugin_id)
        return await self.repository.delete(plugin_id)

    async def list_plugins(
        self,
        project_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Plugin], int]:
        """List plugins, optionally filtered by project."""
        if project_id:
            return await self.repository.get_by_project(project_id, page, page_size)
        return await self.repository.list(page=page, page_size=page_size)

    async def get_enabled_plugins(self, project_id: str) -> list[Plugin]:
        """Get all enabled plugins for a project."""
        return await self.repository.get_enabled(project_id)

    def _validate_manifest(self, manifest: dict) -> None:
        """Validate plugin manifest structure."""
        required_fields = ["name", "version", "description"]
        for field in required_fields:
            if field not in manifest:
                raise PluginValidationException(detail=f"Manifest missing required field: {field}")
