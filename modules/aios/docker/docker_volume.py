"""Docker volumes — list, create and remove persistent volumes."""
from __future__ import annotations

from typing import Any

from modules.aios.docker.docker_client import (
    DockerClient,
    require_docker_action,
)
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class DockerVolume:
    """Volume lifecycle over the docker CLI."""

    def __init__(self, client: DockerClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def list_volumes(self) -> list[dict[str, Any]]:
        require_docker_action("inspect")
        code, out, err = await self._client._run(
            ["volume", "ls", "--format", "{{json .}}"], timeout_s=30.0
        )
        if code != 0:
            raise RuntimeError(f"docker volume ls failed: {err.strip() or out.strip()}")
        self._metrics.increment("docker.volumes.list")
        return self._client.json_lines(out)

    async def create(self, name: str) -> dict[str, Any]:
        require_docker_action("volume")
        code, out, err = await self._client._run(["volume", "create", name], timeout_s=60.0)
        self._metrics.increment("docker.volumes.create")
        return {
            "name": name,
            "ok": code == 0,
            "id": out.strip(),
            "error": err.strip() if code else "",
        }

    async def remove(self, name: str, *, force: bool = False) -> dict[str, Any]:
        require_docker_action("volume")
        args = ["volume", "rm"]
        if force:
            args.append("-f")
        args.append(name)
        code, _, err = await self._client._run(args, timeout_s=60.0)
        self._metrics.increment("docker.volumes.remove")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}


__all__ = ["DockerVolume"]
