from __future__ import annotations

import pytest

from ..llm_cache import LLMCache
from ..llm_context import LLMContextBuilder
from ..llm_engine import LLMEngine
from ..llm_executor import LLMExecutor
from ..llm_factory import LLMFactory
from ..llm_logger import LLMLogger
from ..llm_manager import LLMManager
from ..llm_metrics import LLMMetricsCollector
from ..llm_registry import LLMRegistry
from ..llm_router import LLMRouter
from ..providers.mock_provider import MockProvider


@pytest.fixture
def mock_provider() -> MockProvider:
    return MockProvider("Test response content")


@pytest.fixture
def registry(mock_provider: MockProvider) -> LLMRegistry:
    reg = LLMRegistry()
    reg.register(mock_provider)
    return reg


class TestLLMRegistry:
    def test_register_and_get(self, mock_provider: MockProvider) -> None:
        reg = LLMRegistry()
        name = reg.register(mock_provider)
        assert name == "mock"
        assert reg.get("mock") is mock_provider

    def test_unregister(self, registry: LLMRegistry) -> None:
        assert registry.unregister("mock") is True
        assert registry.get("mock") is None

    def test_list_names(self, registry: LLMRegistry) -> None:
        names = registry.list_names()
        assert "mock" in names

    def test_get_info(self, registry: LLMRegistry) -> None:
        info = registry.get_info("mock")
        assert info is not None
        assert info.name == "mock"

    def test_registry_has_active(self, registry: LLMRegistry) -> None:
        assert "mock" in registry.active_providers


class TestLLMFactory:
    def test_register_and_create(self) -> None:
        factory = LLMFactory()
        factory.register_class("mock", MockProvider)
        provider = factory.create("mock")
        assert isinstance(provider, MockProvider)

    def test_create_with_kwargs(self) -> None:
        factory = LLMFactory()
        factory.register_class("mock", MockProvider)
        provider = factory.create("mock", response_text="Custom response")
        assert isinstance(provider, MockProvider)

    def test_unknown_type(self) -> None:
        factory = LLMFactory()
        with pytest.raises(ValueError):
            factory.create("nonexistent")

    def test_list_types(self) -> None:
        factory = LLMFactory()
        factory.register_class("mock", MockProvider)
        assert "mock" in factory.list_types()


class TestLLMExecutor:
    @pytest.mark.asyncio
    async def test_execute(self, registry: LLMRegistry) -> None:
        executor = LLMExecutor(registry, LLMMetricsCollector(), LLMLogger())
        result = await executor.execute("mock", "Hello")
        assert result["success"] is True
        assert "Test response" in result["content"]

    @pytest.mark.asyncio
    async def test_execute_unknown_provider(self, registry: LLMRegistry) -> None:
        executor = LLMExecutor(registry, LLMMetricsCollector(), LLMLogger())
        result = await executor.execute("unknown", "Hello")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_execute_batch(self, registry: LLMRegistry) -> None:
        executor = LLMExecutor(registry, LLMMetricsCollector(), LLMLogger())
        results = await executor.execute_batch(
            [
                ("mock", "Hi", {}),
                ("mock", "Hello", {}),
            ]
        )
        assert len(results) == 2
        assert all(r["success"] for r in results)


class TestLLMCache:
    @pytest.mark.asyncio
    async def test_set_and_get(self) -> None:
        cache = LLMCache()
        await cache.set("key1", {"content": "hello"})
        result = await cache.get("key1")
        assert result is not None
        assert result["content"] == "hello"

    @pytest.mark.asyncio
    async def test_get_miss(self) -> None:
        cache = LLMCache()
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_invalidate(self) -> None:
        cache = LLMCache()
        await cache.set("key1", {"content": "test"})
        await cache.invalidate("key1")
        assert await cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_clear(self) -> None:
        cache = LLMCache()
        await cache.set("k1", {"a": 1})
        await cache.set("k2", {"b": 2})
        await cache.clear()
        assert cache.size == 0


class TestLLMContextBuilder:
    def test_build(self) -> None:
        builder = LLMContextBuilder()
        ctx = builder.build([{"role": "user", "content": "Hi"}])
        assert "messages" in ctx
        assert ctx["temperature"] == 0.7

    def test_truncate(self) -> None:
        builder = LLMContextBuilder(max_tokens=100)
        ctx = builder.build([{"role": "user", "content": "x" * 1000}])
        truncated = builder.truncate(ctx, 20)
        assert "truncated" in truncated


class TestLLMRouter:
    @pytest.mark.asyncio
    async def test_select_provider(self) -> None:
        registry = LLMRegistry()
        registry.register(MockProvider("test"))
        router = LLMRouter(registry)
        result = await router.select_provider(LLMRouter.STRATEGY_FALLBACK)
        assert result == "mock"

    @pytest.mark.asyncio
    async def test_select(self, registry: LLMRegistry) -> None:
        router = LLMRouter(registry)
        result = await router.select("Hello")
        assert result == "mock"

    def test_set_weight_and_priority(self) -> None:
        registry = LLMRegistry()
        router = LLMRouter(registry)
        router.set_weight("p1", 2.0)
        router.set_priority("p1", 5)


class TestLLMManager:
    def test_initialization(self) -> None:
        manager = LLMManager()
        assert manager.registry is not None
        assert manager.logger is not None
        assert manager.metrics is not None
        assert manager.router is not None
        assert manager.scheduler is not None

    @pytest.mark.asyncio
    async def test_health_check(self) -> None:
        manager = LLMManager()
        health = await manager.health_check()
        assert "healthy" in health


class TestLLMEngine:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        engine = LLMEngine()
        engine._registry.register(MockProvider("Engine test"))
        response = await engine.execute(prompt="Hello", provider="mock", strategy=LLMRouter.STRATEGY_FALLBACK)
        assert isinstance(response.content, str)
        assert response.provider == "mock"

    @pytest.mark.asyncio
    async def test_execute_without_provider(self) -> None:
        engine = LLMEngine()
        engine._registry.register(MockProvider("Auto select"))
        response = await engine.execute(prompt="Hello", strategy=LLMRouter.STRATEGY_FALLBACK)
        assert response.provider == "mock"

    def test_get_cache_info(self) -> None:
        engine = LLMEngine()
        info = engine.get_cache_info()
        assert "size" in info
        assert "default_ttl" in info

    @pytest.mark.asyncio
    async def test_health_check(self) -> None:
        engine = LLMEngine()
        health = await engine.health_check()
        assert "healthy" in health
