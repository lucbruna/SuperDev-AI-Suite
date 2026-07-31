from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .compose import DockerCompose
from .container import DockerContainer
from .image import DockerImage
from .network import DockerNetwork
from .volume import DockerVolume


class DockerTool(BaseTool):
    """Composite Docker tool for container operations."""

    _name = "docker"
    _description = "Docker operations: containers, images, volumes, networks, compose"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._container = DockerContainer()
        self._image = DockerImage()
        self._volume = DockerVolume()
        self._network = DockerNetwork()
        self._compose = DockerCompose()

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        sub_tool = params.get("sub_tool", "")
        action = params.get("action", "")

        if sub_tool == "container" or action in ("list_containers", "start", "stop", "restart"):
            return await self._container.execute(params)
        elif sub_tool == "image" or action in ("list_images", "pull", "build", "push"):
            return await self._image.execute(params)
        elif sub_tool == "volume":
            return await self._volume.execute(params)
        elif sub_tool == "network":
            return await self._network.execute(params)
        elif sub_tool == "compose":
            return await self._compose.execute(params)
        return {"success": False, "error": f"Unknown Docker action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        for tool in (self._container, self._image, self._volume, self._network, self._compose):
            await tool.cleanup()
