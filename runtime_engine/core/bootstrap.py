import asyncio
import logging
import shutil
import sys
from pathlib import Path

from runtime_engine.core.configuration import RuntimeConfig

logger = logging.getLogger(__name__)


class BootstrapError(Exception):
    pass


class Bootstrap:
    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config
        self.sandbox_root: Path | None = None

    async def check_dependencies(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for cmd, name in [("python3", "Python"), ("python", "Python"), ("node", "Node"), ("docker", "Docker")]:
            found = shutil.which(cmd) is not None
            results[name] = found
        results["Python"] = results.get("Python") or results.get("Python3", False)
        return results

    async def initialize_sandbox(self) -> Path:
        base = Path.home() / ".superdev" / "sandbox"
        base.mkdir(parents=True, exist_ok=True)
        self.sandbox_root = base
        logger.info("Sandbox root initialized at %s", base)
        return base

    async def load_config(self) -> RuntimeConfig:
        return self.config

    async def run(self) -> dict[str, bool]:
        deps = await self.check_dependencies()
        if not deps.get("Python"):
            raise BootstrapError("Python is required but not found")
        await self.initialize_sandbox()
        return deps
