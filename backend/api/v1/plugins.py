from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.rbac import Action, Resource, require_permission
from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.plugins.plugin_manager import plugin_manager
from backend.plugins.plugin_registry import plugin_registry

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class PluginInstallRequest(BaseModel):
    slug: str


class PluginConfigUpdate(BaseModel):
    settings: dict = {}


class PluginRegistryResponse(BaseModel):
    name: str
    slug: str
    version: str
    description: str
    author: str
    plugin_type: str
    tags: list[str]
    downloads: int
    rating: float
    is_official: bool


class PluginInstalledResponse(BaseModel):
    name: str
    slug: str
    version: str
    status: str
    config: dict


@router.get("/registry", response_model=list[PluginRegistryResponse])
async def list_registry_plugins(
    plugin_type: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[PluginRegistryResponse]:
    plugins = plugin_registry.list_plugins(
        plugin_type=plugin_type,
        tag=tag,
        search=search,
    )
    return [
        PluginRegistryResponse(
            name=p.name,
            slug=p.slug,
            version=p.version,
            description=p.description,
            author=p.author,
            plugin_type=p.plugin_type,
            tags=p.tags,
            downloads=p.downloads,
            rating=p.rating,
            is_official=p.is_official,
        )
        for p in plugins
    ]


@router.get("/registry/popular", response_model=list[PluginRegistryResponse])
async def get_popular_plugins(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.PLUGINS, Action.READ)),
) -> list[PluginRegistryResponse]:
    plugins = plugin_registry.get_popular(limit)
    return [
        PluginRegistryResponse(
            name=p.name,
            slug=p.slug,
            version=p.version,
            description=p.description,
            author=p.author,
            plugin_type=p.plugin_type,
            tags=p.tags,
            downloads=p.downloads,
            rating=p.rating,
            is_official=p.is_official,
        )
        for p in plugins
    ]


@router.get("/registry/categories")
async def get_plugin_categories(
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    return plugin_registry.get_categories()


@router.get("/installed", response_model=list[PluginInstalledResponse])
async def list_installed_plugins(
    db: AsyncSession = Depends(get_db),
) -> list[PluginInstalledResponse]:
    plugins = plugin_manager.list_plugins()
    return [
        PluginInstalledResponse(
            name=p["metadata"]["name"],
            slug=p["metadata"]["slug"],
            version=p["metadata"]["version"],
            status=p["status"],
            config=p["config"],
        )
        for p in plugins
    ]


@router.post("/install", response_model=PluginInstalledResponse, status_code=status.HTTP_201_CREATED)
async def install_plugin(
    request: PluginInstallRequest,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.PLUGINS, Action.CREATE)),
) -> PluginInstalledResponse:

    entry = plugin_registry.get(request.slug)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin not found in registry: {request.slug}",
        )

    from backend.plugins.base_plugin import PluginMetadata, PluginType

    metadata = PluginMetadata(
        name=entry.name,
        slug=entry.slug,
        version=entry.version,
        description=entry.description,
        author=entry.author,
        plugin_type=PluginType(entry.plugin_type),
        tags=entry.tags,
    )

    from backend.plugins.base_plugin import BasePlugin

    class SimplePlugin(BasePlugin):
        async def on_activate(self) -> None:
            pass

        async def on_deactivate(self) -> None:
            pass

    try:
        plugin = await plugin_manager.install_plugin(metadata, SimplePlugin)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    return PluginInstalledResponse(
        name=plugin.metadata.name,
        slug=plugin.metadata.slug,
        version=plugin.metadata.version,
        status=plugin.status.value,
        config=plugin.config.settings,
    )


@router.post("/{slug}/enable", status_code=status.HTTP_200_OK)
async def enable_plugin(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.PLUGINS, Action.UPDATE)),
) -> dict:

    enabled = await plugin_manager.enable_plugin(slug)
    if not enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin not found: {slug}",
        )
    return {"slug": slug, "status": "enabled"}


@router.post("/{slug}/disable", status_code=status.HTTP_200_OK)
async def disable_plugin(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.PLUGINS, Action.UPDATE)),
) -> dict:

    disabled = await plugin_manager.disable_plugin(slug)
    if not disabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin not found: {slug}",
        )
    return {"slug": slug, "status": "disabled"}


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def uninstall_plugin(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.PLUGINS, Action.DELETE)),
) -> None:

    uninstalled = await plugin_manager.uninstall_plugin(slug)
    if not uninstalled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin not found: {slug}",
        )


@router.put("/{slug}/config")
async def update_plugin_config(
    slug: str,
    request: PluginConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.PLUGINS, Action.UPDATE)),
) -> dict:

    updated = await plugin_manager.update_plugin_config(slug, request.settings)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin not found: {slug}",
        )
    return {"slug": slug, "config": request.settings}
