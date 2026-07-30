from __future__ import annotations

import pytest

from .reasoning_context import ReasoningContext
from .reasoning_engine import ReasoningEngine
from .reasoning_memory import ReasoningMemory
from .reasoning_models import ReasoningResult


@pytest.fixture
def engine() -> ReasoningEngine:
    return ReasoningEngine()


@pytest.fixture
def context() -> ReasoningContext:
    return ReasoningContext(query="test query", context_id="test-001")


@pytest.mark.asyncio
async def test_reasoning_engine_returns_result(engine: ReasoningEngine, context: ReasoningContext) -> None:
    result = await engine.reason(context)
    assert isinstance(result, ReasoningResult)
    assert result.context_id == "test-001"


@pytest.mark.asyncio
async def test_reasoning_memory() -> None:
    memory = ReasoningMemory()
    await memory.store("key1", "value1")
    val = await memory.retrieve("key1")
    assert val == "value1"
    await memory.forget("key1")
    val = await memory.retrieve("key1")
    assert val is None


def test_reasoning_context_defaults() -> None:
    ctx = ReasoningContext()
    assert ctx.query == ""
    assert ctx.constraints == []
    assert ctx.context_id == ""
