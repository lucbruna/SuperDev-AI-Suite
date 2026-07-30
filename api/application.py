from __future__ import annotations

from typing import Any

from .app import APIApplication


class APIEngine:
    """Convenience wrapper for creating and running an API application."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        self._host = host
        self._port = port
        self._app: APIApplication | None = None

    async def run(self) -> None:
        self._app = APIApplication()

        self._app.startup.add_hook("config", lambda m: m.logger.info("Config loaded"))
        self._app.startup.add_hook("metrics", lambda m: m.metrics.increment("server.starts"))

        await self._app.start(host=self._host, port=self._port)

    async def stop(self) -> None:
        if self._app is not None:
            await self._app.stop()

    @property
    def app(self) -> APIApplication | None:
        return self._app

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self._host,
            "port": self._port,
            "running": self._app is not None,
        }
