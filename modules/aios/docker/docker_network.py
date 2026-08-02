"""Docker networks — list, create, remove and attach networks."""
from __future__ import annotations

from typing import Any

from modules.aios.docker.docker_client import (
    DockerClient,
    require_docker_action,
)
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class DockerNetwork:
    """Network lifecycle over the docker CLI."""

    def __init__(self, client: DockerClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def list_networks(self) -> list[dict[str, Any]]:
        require_docker_action("inspect")
        code, out, err = await self._client._run(
            ["network", "ls", "--format", "{{json .}}"], timeout_s=30.0
        )
        if code != 0:
            raise RuntimeError(f"docker network ls failed: {err.strip() or out.strip()}")
        self._metrics.increment("docker.networks.list")
        return self._client.json_lines(out)

    async def create(self, name: str, *, driver: str = "bridge") -> dict[str, Any]:
        require_docker_action("network")
        code, out, err = await self._client._run(
            ["network", "create", "-d", driver, name], timeout_s=60.0
        )
        self._metrics.increment("docker.networks.create")
        return {
            "name": name,
            "ok": code == 0,
            "id": out.strip(),
            "error": err.strip() if code else "",
        }

    async def remove(self, name: str) -> dict[str, Any]:
        require_docker_action("network")
        code, _, err = await self._client._run(["network", "rm", name], timeout_s=60.0)
        self._metrics.increment("docker.networks.remove")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def connect(self, container: str, network: str) -> dict[str, Any]:
        require_docker_action("network")
        code, _, err = await self._client._run(
            ["network", "connect", network, container], timeout_s=60.0
        )
        return {"container": container, "network": network, "ok": code == 0, "error": err.strip() if code else ""}

    async def disconnect(self, container: str, network: str) -> dict[str, Any]:
        require_docker_action("network")
        code, _, err = await self._client._run(
            ["network", "disconnect", network, container], timeout_s=60.0
        )
        return {"container": container, "network": network, "ok": code == 0, "error": err.strip() if code else ""}


__all__ = ["DockerNetwork"]
