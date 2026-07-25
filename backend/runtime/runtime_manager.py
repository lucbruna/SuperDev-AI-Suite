from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from backend.runtime.base_runtime import (
    BaseRuntime,
    ExecutionResult,
    Language,
    RuntimeConfig,
    RuntimeStatus,
)
from backend.runtime.node_runtime import NodeRuntime
from backend.runtime.python_runtime import PythonRuntime
from backend.runtime.shell_runtime import ShellRuntime
from backend.websocket.events import EventBuilder
from backend.websocket.manager import manager


class RuntimeManager:
    """Manages multiple language runtimes and orchestrates execution."""

    def __init__(self):
        self._runtimes: dict[Language, BaseRuntime] = {
            Language.PYTHON: PythonRuntime(),
            Language.NODEJS: NodeRuntime(),
            Language.SHELL: ShellRuntime(),
        }
        self._running: dict[str, asyncio.Task] = {}

    def register_runtime(self, language: Language, runtime: BaseRuntime) -> None:
        self._runtimes[language] = runtime

    def get_runtime(self, language: Language) -> BaseRuntime | None:
        return self._runtimes.get(language)

    def detect_language(self, filename: str) -> Language | None:
        ext_map = {
            ".py": Language.PYTHON,
            ".js": Language.NODEJS,
            ".ts": Language.NODEJS,
            ".mjs": Language.NODEJS,
            ".sh": Language.SHELL,
            ".bash": Language.SHELL,
        }
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang
        return None

    async def execute(
        self,
        config: RuntimeConfig,
        run_id: str,
        user_id: str | None = None,
    ) -> ExecutionResult:
        runtime = self._runtimes.get(config.language)
        if not runtime:
            return ExecutionResult(
                run_id=run_id,
                status=RuntimeStatus.FAILED,
                error=f"Unsupported language: {config.language}",
            )

        event = EventBuilder.runtime_start(run_id, config.language.value)
        event.user_id = user_id
        await manager.broadcast_all(event.to_dict())

        result = await runtime.execute(config, run_id)

        if result.status == RuntimeStatus.COMPLETED:
            complete_event = EventBuilder.runtime_log(run_id, "Execution completed successfully")
        else:
            complete_event = EventBuilder.runtime_log(run_id, f"Execution failed: {result.error or result.stderr[:200]}")
        complete_event.user_id = user_id
        await manager.broadcast_all(complete_event.to_dict())

        return result

    async def stream(
        self,
        config: RuntimeConfig,
        run_id: str,
        user_id: str | None = None,
    ) -> AsyncIterator[str]:
        runtime = self._runtimes.get(config.language)
        if not runtime:
            yield f"Error: Unsupported language: {config.language}\n"
            return

        async for line in runtime.stream(config, run_id):
            yield line

    async def cancel(self, run_id: str) -> bool:
        task = self._running.get(run_id)
        if task and not task.done():
            task.cancel()
            return True
        return False

    async def close(self) -> None:
        for runtime in self._runtimes.values():
            await runtime.close()
        self._runtimes.clear()


runtime_manager = RuntimeManager()
