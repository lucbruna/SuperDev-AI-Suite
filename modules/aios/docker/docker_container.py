"""Docker containers — run, start, stop, remove and inspect containers."""
from __future__ import annotations

from typing import Any

from modules.aios.docker.docker_client import (
    DockerClient,
    require_docker_action,
)
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class DockerContainer:
    """Container lifecycle over the docker CLI."""

    def __init__(self, client: DockerClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def run(
        self,
        image: str,
        *,
        name: str | None = None,
        command: list[str] | None = None,
        detach: bool = False,
        remove: bool = False,
        network: str | None = None,
    ) -> dict[str, Any]:
        require_docker_action("run")
        args = ["run"]
        if detach:
            args.append("-d")
        if remove:
            args.append("--rm")
        if name is not None:
            args += ["--name", name]
        if network is not None:
            args += ["--network", network]
        args.append(image)
        if command:
            args += command
        code, out, err = await self._client._run(args, timeout_s=120.0)
        self._metrics.increment("docker.containers.run")
        self._client._logger.log(
            "docker", f"run {image}", payload={"ok": code == 0}
        )
        ref = name or (out.strip() if code == 0 else "")
        return {
            "image": image,
            "container": ref,
            "ok": code == 0,
            "error": err.strip() if code else "",
        }

    async def start(self, container: str) -> dict[str, Any]:
        require_docker_action("run")
        code, _, err = await self._client._run(["start", container], timeout_s=60.0)
        self._metrics.increment("docker.containers.start")
        return {"container": container, "ok": code == 0, "error": err.strip() if code else ""}

    async def stop(self, container: str, *, timeout_s: float | None = None) -> dict[str, Any]:
        require_docker_action("run")
        args = ["stop"]
        if timeout_s is not None:
            args += ["-t", str(int(timeout_s))]
        args.append(container)
        code, _, err = await self._client._run(args, timeout_s=60.0)
        self._metrics.increment("docker.containers.stop")
        return {"container": container, "ok": code == 0, "error": err.strip() if code else ""}

    async def remove(self, container: str, *, force: bool = True) -> dict[str, Any]:
        require_docker_action("remove")
        args = ["rm"]
        if force:
            args.append("-f")
        args.append(container)
        code, _, err = await self._client._run(args, timeout_s=60.0)
        self._metrics.increment("docker.containers.remove")
        return {"container": container, "ok": code == 0, "error": err.strip() if code else ""}

    async def list_containers(self, *, all: bool = False) -> list[dict[str, Any]]:
        require_docker_action("inspect")
        args = ["ps"]
        if all:
            args.append("-a")
        args += ["--format", "{{json .}}"]
        code, out, err = await self._client._run(args, timeout_s=30.0)
        if code != 0:
            raise RuntimeError(f"docker ps failed: {err.strip() or out.strip()}")
        self._metrics.increment("docker.containers.list")
        return self._client.json_lines(out)

    async def inspect(self, container: str) -> dict[str, Any]:
        require_docker_action("inspect")
        code, out, err = await self._client._run(["inspect", container], timeout_s=30.0)
        if code != 0:
            raise RuntimeError(f"docker inspect failed: {err.strip() or out.strip()}")
        return self._client.first_json(out)

    async def exec(self, container: str, command: list[str]) -> tuple[int, str, str]:
        require_docker_action("run")
        return await self._client._run(["exec", container, *command], timeout_s=60.0)


__all__ = ["DockerContainer"]
