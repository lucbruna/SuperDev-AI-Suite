"""Podman runtime — docker-compatible engine facade (Volume 12, Fase 15)."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.podman.podman_client import (
    PodmanClient,
    PodmanUnavailableError,
    require_podman_action,
)


class PodmanRuntime:
    """Facade over the podman integration.

    Stateless: delegates to the docker-compatible podman CLI. ``close`` is a
    no-op; containers are NOT killed here. Falls back gracefully when podman
    is not installed (:meth:`available` returns False).
    """

    def __init__(self) -> None:
        self.client = PodmanClient()
        self._logger = get_kernel_logger()

    async def available(self) -> bool:
        return await self.client.ping()

    async def version(self) -> dict[str, Any]:
        return await self.client.version()

    async def info(self) -> dict[str, Any]:
        return await self.client.info()

    async def run(self, image: str, *args: str) -> dict[str, Any]:
        require_podman_action("run")
        code, out, err = await self.client._run(["run", *args, image], timeout_s=120.0)
        return {
            "image": image,
            "ok": code == 0,
            "id": out.strip(),
            "error": err.strip() if code else "",
        }

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort aggregate state; degrades cleanly when podman is absent."""
        state: dict[str, Any] = {
            "available": False,
            "version": {},
            "info": {},
        }
        try:
            state["available"] = await self.client.ping()
        except PodmanUnavailableError:
            return state
        if not state["available"]:
            return state
        try:
            state["version"] = await self.client.version()
        except (PodmanUnavailableError, RuntimeError):
            state["version"] = {}
        try:
            state["info"] = await self.client.info()
        except (PodmanUnavailableError, RuntimeError):
            state["info"] = {}
        return state

    async def close(self) -> None:
        """No-op — the podman runtime is stateless. Containers are not killed."""


_podman_runtime: PodmanRuntime | None = None


def get_podman_runtime() -> PodmanRuntime:
    global _podman_runtime
    if _podman_runtime is None:
        _podman_runtime = PodmanRuntime()
    return _podman_runtime


__all__ = ["PodmanRuntime", "get_podman_runtime"]
