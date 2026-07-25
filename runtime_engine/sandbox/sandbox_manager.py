from __future__ import annotations

import logging
from typing import Any

from runtime_engine.sandbox.sandbox import DefaultSandbox, Sandbox
from runtime_engine.sandbox.sandbox_policy import SandboxPolicy
from runtime_engine.core.configuration import RuntimeConfig

logger = logging.getLogger(__name__)


class SandboxManager:
    def __init__(self) -> None:
        self._sandboxes: dict[str, Sandbox] = {}
        self._max_sandboxes: int = 50

    async def create_sandbox(self, config: RuntimeConfig | None = None) -> str:
        if len(self._sandboxes) >= self._max_sandboxes:
            raise RuntimeError(f"Max sandboxes reached ({self._max_sandboxes})")
        sandbox = DefaultSandbox()
        sandbox_id = await sandbox.create()
        self._sandboxes[sandbox_id] = sandbox
        return sandbox_id

    async def get_sandbox(self, sandbox_id: str) -> Sandbox | None:
        return self._sandboxes.get(sandbox_id)

    async def destroy_sandbox(self, sandbox_id: str) -> bool:
        sandbox = self._sandboxes.pop(sandbox_id, None)
        if sandbox is None:
            return False
        await sandbox.destroy()
        return True

    async def destroy_all(self) -> None:
        for sandbox_id, sandbox in list(self._sandboxes.items()):
            await sandbox.destroy()
        self._sandboxes.clear()

    def list_active(self) -> list[str]:
        return list(self._sandboxes.keys())

    def active_count(self) -> int:
        return len(self._sandboxes)
