"""Docker cleanup — prune unused containers, images, networks and volumes."""
from __future__ import annotations

from typing import Any

from modules.aios.docker.docker_client import (
    DockerClient,
    require_docker_action,
)
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class DockerCleanup:
    """Resource reclamation over the docker CLI."""

    def __init__(self, client: DockerClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def prune_containers(self) -> dict[str, Any]:
        require_docker_action("prune")
        code, _, err = await self._client._run(["container", "prune", "-f"], timeout_s=60.0)
        self._metrics.increment("docker.cleanup.containers")
        return {"target": "containers", "ok": code == 0, "error": err.strip() if code else ""}

    async def prune_images(self) -> dict[str, Any]:
        require_docker_action("prune")
        code, _, err = await self._client._run(["image", "prune", "-f"], timeout_s=60.0)
        self._metrics.increment("docker.cleanup.images")
        return {"target": "images", "ok": code == 0, "error": err.strip() if code else ""}

    async def prune_networks(self) -> dict[str, Any]:
        require_docker_action("prune")
        code, _, err = await self._client._run(["network", "prune", "-f"], timeout_s=60.0)
        self._metrics.increment("docker.cleanup.networks")
        return {"target": "networks", "ok": code == 0, "error": err.strip() if code else ""}

    async def prune_volumes(self) -> dict[str, Any]:
        require_docker_action("prune")
        code, _, err = await self._client._run(["volume", "prune", "-f"], timeout_s=60.0)
        self._metrics.increment("docker.cleanup.volumes")
        return {"target": "volumes", "ok": code == 0, "error": err.strip() if code else ""}

    async def remove_stopped(self) -> dict[str, Any]:
        require_docker_action("remove")
        code, out, err = await self._client._run(["ps", "-aq"], timeout_s=30.0)
        ids = [line for line in out.splitlines() if line.strip()]
        removed = 0
        for cid in ids:
            rc, _, rerr = await self._client._run(["rm", "-f", cid], timeout_s=60.0)
            if rc == 0:
                removed += 1
            if rerr.strip():
                err = f"{err.strip()} {rerr.strip()}".strip()
        self._metrics.increment("docker.cleanup.stopped", removed)
        return {"target": "stopped", "ok": code == 0, "removed": removed, "error": err.strip() if code else ""}


__all__ = ["DockerCleanup"]
