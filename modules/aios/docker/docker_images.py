"""Docker images — pull, build, list and remove images."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.aios.docker.docker_client import (
    DockerClient,
    require_docker_action,
)
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class DockerImages:
    """Image lifecycle over the docker CLI."""

    def __init__(self, client: DockerClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def list_images(self) -> list[dict[str, Any]]:
        require_docker_action("inspect")
        code, out, err = await self._client._run(
            ["images", "--format", "{{json .}}"], timeout_s=30.0
        )
        if code != 0:
            raise RuntimeError(f"docker images failed: {err.strip() or out.strip()}")
        self._metrics.increment("docker.images.list")
        return self._client.json_lines(out)

    async def pull(self, name: str) -> dict[str, Any]:
        require_docker_action("pull")
        code, out, err = await self._client._run(
            ["pull", name], timeout_s=300.0
        )
        self._metrics.increment("docker.images.pull")
        self._client._logger.log(
            "docker", f"pull {name}", payload={"ok": code == 0}
        )
        return {"image": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def build(
        self, tag: str, context: str | Path, dockerfile: str | None = None
    ) -> dict[str, Any]:
        require_docker_action("build")
        args = ["build", "-t", tag]
        if dockerfile is not None:
            args += ["-f", dockerfile]
        args.append(str(context))
        code, out, err = await self._client._run(args, timeout_s=300.0)
        self._metrics.increment("docker.images.build")
        self._client._logger.log(
            "docker", f"build {tag}", payload={"ok": code == 0}
        )
        return {"tag": tag, "ok": code == 0, "error": err.strip() if code else ""}

    async def remove(self, name: str, *, force: bool = True) -> dict[str, Any]:
        require_docker_action("remove")
        args = ["rmi"]
        if force:
            args.append("-f")
        args.append(name)
        code, out, err = await self._client._run(args, timeout_s=60.0)
        self._metrics.increment("docker.images.remove")
        return {"image": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def exists(self, name: str) -> bool:
        require_docker_action("inspect")
        rows = await self.list_images()
        wanted = name if ":" in name else f"{name}:latest"
        return any(r.get("Repository") and f"{r['Repository']}:{r.get('Tag', '')}" == wanted for r in rows)


__all__ = ["DockerImages"]
