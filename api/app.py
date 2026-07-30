from __future__ import annotations

from typing import Any

from .api_manager import APIManager
from .server import APIServer
from .shutdown import APIShutdown
from .startup import APIStartup


class APIApplication:
    """Top-level application container for the API Engine.

    Wires together the manager, server, startup, and shutdown sequences
    into a single entry point.
    """

    def __init__(self) -> None:
        self.manager = APIManager()
        self.server = APIServer(self.manager.runtime)
        self.startup = APIStartup(self.manager)
        self.shutdown = APIShutdown(self.manager)

    async def start(self, host: str | None = None, port: int | None = None) -> None:
        await self.startup.run()
        await self.server.serve(host=host, port=port)

    async def stop(self) -> None:
        await self.server.stop()
        await self.shutdown.run()

    def to_dict(self) -> dict[str, Any]:
        return {
            "manager": self.manager.to_dict(),
            "server": self.server.to_dict(),
            "startup": self.startup.to_dict(),
            "shutdown": self.shutdown.to_dict(),
        }
