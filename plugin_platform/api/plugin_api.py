from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from ..registry.plugin_registry import PluginRegistry
from ..installer.install import PluginInstaller
from ..installer.uninstall import PluginUninstaller
from ..installer.upgrade import PluginUpgrader
from ..marketplace.marketplace_client import MarketplaceClient


class InstallRequest(BaseModel):
    source: str


def create_plugin_api(
    registry: PluginRegistry,
    installer: PluginInstaller,
    uninstaller: PluginUninstaller,
    upgrader: PluginUpgrader,
    marketplace_client: MarketplaceClient | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/plugins", tags=["plugins"])
    mc = marketplace_client or MarketplaceClient()

    @router.post("/install")
    async def install_plugin(body: InstallRequest) -> dict[str, Any]:
        try:
            manifest = installer.install(body.source)
            return {"success": True, "manifest": manifest}
        except (ValueError, FileExistsError, FileNotFoundError) as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/{name}/uninstall")
    async def uninstall_plugin(name: str) -> dict[str, bool]:
        result = uninstaller.uninstall(name)
        if not result:
            raise HTTPException(status_code=404, detail=f"Plugin '{name}' not found")
        return {"success": True}

    @router.get("/")
    async def list_plugins(category: str | None = None) -> list[dict[str, Any]]:
        return registry.list(category=category)

    @router.get("/{name}")
    async def get_plugin(name: str) -> dict[str, Any]:
        entry = registry.get(name)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Plugin '{name}' not found")
        return entry

    @router.put("/{name}/enable")
    async def enable_plugin(name: str) -> dict[str, bool]:
        entry = registry.get(name)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Plugin '{name}' not found")
        registry._plugins[name]["enabled"] = True
        return {"success": True}

    @router.put("/{name}/disable")
    async def disable_plugin(name: str) -> dict[str, bool]:
        entry = registry.get(name)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Plugin '{name}' not found")
        registry._plugins[name]["enabled"] = False
        return {"success": True}

    @router.post("/{name}/upgrade")
    async def upgrade_plugin(name: str, new_version: str) -> dict[str, bool]:
        try:
            result = upgrader.upgrade(name, new_version)
            return {"success": result}
        except (KeyError, ValueError) as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router


def create_marketplace_router(
    marketplace_client: MarketplaceClient | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/marketplace", tags=["marketplace"])
    mc = marketplace_client or MarketplaceClient()

    @router.get("/search")
    async def search_plugins(q: str = "", cat: str = "") -> list[dict[str, Any]]:
        return await mc.search(query=q, category=cat)

    @router.get("/featured")
    async def featured_plugins() -> list[dict[str, Any]]:
        return await mc.get_featured()

    return router