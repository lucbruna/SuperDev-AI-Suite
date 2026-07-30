from __future__ import annotations

from typing import Any

from .chain_builder import ChainBuilder
from .chain_executor import ChainExecutor
from .chain_memory import ChainMemory
from .chain_validator import ChainValidator


class ChainEngine:
    """Core chain-of-thought reasoning engine."""

    def __init__(
        self,
        builder: ChainBuilder | None = None,
        executor: ChainExecutor | None = None,
        memory: ChainMemory | None = None,
        validator: ChainValidator | None = None,
    ):
        self._builder = builder or ChainBuilder()
        self._executor = executor or ChainExecutor()
        self._memory = memory or ChainMemory()
        self._validator = validator or ChainValidator()

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        chain = await self._builder.build(context)
        validated = await self._validator.validate(chain)
        if not validated.get("valid", False):
            return {"success": False, "errors": validated.get("errors", [])}
        result = await self._executor.execute(chain, context)
        await self._memory.save(chain, result)
        return {"success": True, "chain": chain, "result": result}

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return await self.process(context)
