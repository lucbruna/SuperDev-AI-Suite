"""Docker runtime — facade composing client, images, containers, networks,
volumes, logs and cleanup into one kernel-integrated surface."""
from __future__ import annotations

from typing import Any

from modules.aios.docker.docker_client import (
    DockerClient,
    DockerUnavailableError,
)
from modules.aios.docker.docker_cleanup import DockerCleanup
from modules.aios.docker.docker_container import DockerContainer
from modules.aios.docker.docker_images import DockerImages
from modules.aios.docker.docker_logs import DockerLogs
from modules.aios.docker.docker_network import DockerNetwork
from modules.aios.docker.docker_volume import DockerVolume
from modules.aios.kernel.kernel_logger import get_kernel_logger


class DockerRuntime:
    """Facade over the docker integration (Volume 12, Fase 14).

    Stateless: sub-managers are plain CLI wrappers. ``close`` is a no-op —
    containers are intentionally NOT killed here; use :class:`DockerCleanup`.
    """

    def __init__(self) -> None:
        self.client = DockerClient()
        self.images = DockerImages(self.client)
        self.containers = DockerContainer(self.client)
        self.logs = DockerLogs(self.client)
        self.network = DockerNetwork(self.client)
        self.volumes = DockerVolume(self.client)
        self.cleanup = DockerCleanup(self.client)
        self._logger = get_kernel_logger()

    async def available(self) -> bool:
        return await self.client.ping()

    async def version(self) -> dict[str, Any]:
        return await self.client.version()

    async def info(self) -> dict[str, Any]:
        return await self.client.info()

    async def run(self, image: str, **kwargs: Any) -> dict[str, Any]:
        return await self.containers.run(image, **kwargs)

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort aggregate state; each section degrades to [] on error."""
        state: dict[str, Any] = {
            "available": False,
            "version": {},
            "images": [],
            "containers": [],
            "networks": [],
            "volumes": [],
        }
        try:
            state["available"] = await self.client.ping()
        except DockerUnavailableError:
            return state
        if not state["available"]:
            return state

        async def _safe(coro: Any) -> list[dict[str, Any]]:
            try:
                return await coro
            except Exception:  # noqa: BLE001
                return []

        try:
            state["version"] = await self.client.version()
        except (DockerUnavailableError, RuntimeError):
            state["version"] = {}
        state["images"] = await _safe(self.images.list_images())
        state["containers"] = await _safe(self.containers.list_containers(all=True))
        state["networks"] = await _safe(self.network.list_networks())
        state["volumes"] = await _safe(self.volumes.list_volumes())
        return state

    async def close(self) -> None:
        """No-op — the docker runtime is stateless. Containers are not killed."""


_docker_runtime: DockerRuntime | None = None


def get_docker_runtime() -> DockerRuntime:
    global _docker_runtime
    if _docker_runtime is None:
        _docker_runtime = DockerRuntime()
    return _docker_runtime


__all__ = ["DockerRuntime", "get_docker_runtime"]
