from __future__ import annotations

import logging

from runtime_engine.runtime.runtime import BaseRuntime, ExecutionResult
from runtime_engine.runtime.runtime_context import RuntimeContext
from runtime_engine.core.registry import RuntimeRegistry
from runtime_engine.core.configuration import RuntimeConfig
from runtime_engine.sandbox.sandbox import DefaultSandbox

logger = logging.getLogger(__name__)


class RuntimeExecutor:
    def __init__(self, registry: RuntimeRegistry, config: RuntimeConfig) -> None:
        self._registry = registry
        self._config = config

    async def execute(self, context: RuntimeContext, code_input: str) -> ExecutionResult:
        runtime_cls = self._registry.get(context.language)
        if runtime_cls is None:
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr="",
                duration=0.0,
                error=f"Unsupported language: {context.language}",
            )

        runtime: BaseRuntime = runtime_cls(self._config)
        sandbox = DefaultSandbox()

        try:
            context.ensure_work_dir()
            if self._config.sandbox_enabled:
                sandbox_id = await sandbox.create()
                logger.debug("Sandbox %s created for session %s", sandbox_id, context.session_id)

            result = await runtime.execute(code_input, context.language, self._config)
            return result
        except Exception as e:
            logger.error("Execution failed for session %s: %s", context.session_id, e)
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration=0.0,
                error=str(e),
            )
        finally:
            if self._config.sandbox_enabled:
                await sandbox.destroy()
