from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from ..llm_factory import LLMFactory
from ..llm_manager import LLMManager
from ..llm_registry import LLMRegistry
from ..providers.base_provider import (
    ProviderError,
    ProviderErrorCode,
    TokenBucket,
    estimate_cost,
)
from ..providers.mock_provider import MockProvider

# =========================================================================
# BaseLLMProvider
# =========================================================================


class TestBaseProvider:
    @pytest.mark.asyncio
    async def test_ensure_deterministic(self) -> None:
        p = MockProvider()
        kwargs = p._ensure_deterministic({"temperature": 0.7})
        assert kwargs["temperature"] == 0.0
        assert kwargs["top_p"] == 1.0

    @pytest.mark.asyncio
    async def test_stats_tracking(self) -> None:
        p = MockProvider()
        result = await p.generate("test prompt")
        assert result["call_count"] == 1
        stats = p.stats()
        assert stats["call_count"] == 1
        assert stats["total_cost_usd"] >= 0

    @pytest.mark.asyncio
    async def test_multiple_calls_increment_count(self) -> None:
        p = MockProvider()
        await p.generate("first")
        await p.generate("second")
        await p.generate("third")
        stats = p.stats()
        assert stats["call_count"] == 3

    def test_to_dict_includes_stats(self) -> None:
        p = MockProvider()
        d = p.to_dict()
        assert "call_count" in d
        assert "name" in d
        assert d["name"] == "mock"


# =========================================================================
# TokenBucket
# =========================================================================


class TestTokenBucket:
    @pytest.mark.asyncio
    async def test_immediate_when_tokens_available(self) -> None:
        bucket = TokenBucket(rate=100, capacity=10)
        wait = await bucket.acquire()
        assert wait == 0.0

    @pytest.mark.asyncio
    async def test_rate_limits(self) -> None:
        bucket = TokenBucket(rate=0.1, capacity=1)  # 1 token per 10s
        wait1 = await bucket.acquire()
        assert wait1 == 0.0  # first is free
        wait2 = await bucket.acquire()
        assert wait2 > 0.0  # must wait for refill


# =========================================================================
# Error Handling
# =========================================================================


class TestProviderError:
    def test_classify_auth_error(self) -> None:
        exc = Exception("Authentication failed: invalid API key")
        err = ProviderError.from_exception(exc, provider="test")
        assert err.code == ProviderErrorCode.AUTH

    def test_classify_rate_limit(self) -> None:
        exc = Exception("429 Too Many Requests: rate limit exceeded")
        err = ProviderError.from_exception(exc, provider="test")
        assert err.code == ProviderErrorCode.RATE_LIMIT

    def test_classify_timeout(self) -> None:
        exc = Exception("timed out after 30s")
        err = ProviderError.from_exception(exc, provider="test")
        assert err.code == ProviderErrorCode.TIMEOUT

    def test_classify_unknown(self) -> None:
        exc = Exception("something unexpected happened")
        err = ProviderError.from_exception(exc, provider="test")
        assert err.code == ProviderErrorCode.API_ERROR


# =========================================================================
# Cost Estimation
# =========================================================================


class TestCostEstimation:
    def test_estimate_openai_gpt4o(self) -> None:
        cost = estimate_cost("openai", "gpt-4o", 100, 50)
        assert cost > 0
        assert round(cost, 6) == 0.00075  # (100 * 0.0025 / 1000) + (50 * 0.01 / 1000)

    def test_estimate_unknown_provider(self) -> None:
        cost = estimate_cost("unknown", "foo", 100, 50)
        assert cost == 0.0


# =========================================================================
# MockProvider (canned)
# =========================================================================


class TestMockProvider:
    @pytest.mark.asyncio
    async def test_generate(self) -> None:
        p = MockProvider("Hello world")
        result = await p.generate("test prompt")
        assert result["success"] is True
        assert result["content"] == "Hello world"

    @pytest.mark.asyncio
    async def test_generate_stream(self) -> None:
        p = MockProvider("Hello world")
        stream = await p.generate_stream("test")
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        assert len(chunks) > 0

    def test_call_count(self) -> None:
        p = MockProvider("test")
        assert p.call_count == 0

    def test_set_response(self) -> None:
        p = MockProvider()
        p.set_response("custom response")
        assert p.to_dict()["response_preview"] == "custom response"


# =========================================================================
# LLMFactory
# =========================================================================


class TestLLMFactoryExtended:
    def test_create_with_defaults(self) -> None:
        factory = LLMFactory()
        factory.register_class("mock", MockProvider)
        provider = factory.create("mock")
        assert isinstance(provider, MockProvider)

    def test_create_with_kwargs(self) -> None:
        factory = LLMFactory()
        factory.register_class("mock", MockProvider)
        provider = factory.create("mock", response_text="custom")
        assert isinstance(provider, MockProvider)

    def test_list_types(self) -> None:
        factory = LLMFactory()
        factory.register_class("mock", MockProvider)
        factory.register_class("custom", MockProvider)
        types = factory.list_types()
        assert "mock" in types
        assert "custom" in types
        assert factory.type_count == 2

    def test_unknown_type_raises(self) -> None:
        factory = LLMFactory()
        with pytest.raises(ValueError):
            factory.create("nonexistent")


# =========================================================================
# LLMRegistry
# =========================================================================


class TestLLMRegistryExtended:
    @pytest.mark.asyncio
    async def test_register_provider(self) -> None:
        registry = LLMRegistry()
        p = MockProvider()
        name = registry.register(p)
        assert name == "mock"
        assert registry.provider_count == 1

    @pytest.mark.asyncio
    async def test_get_provider(self) -> None:
        registry = LLMRegistry()
        p = MockProvider()
        registry.register(p)
        retrieved = registry.get("mock")
        assert retrieved is p

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self) -> None:
        registry = LLMRegistry()
        assert registry.get("nonexistent") is None

    @pytest.mark.asyncio
    async def test_active_providers(self) -> None:
        registry = LLMRegistry()
        p = MockProvider()
        registry.register(p)
        active = registry.active_providers
        assert "mock" in active


# =========================================================================
# LLMManager
# =========================================================================


class TestLLMManagerExtended:
    @pytest.mark.asyncio
    async def test_initialization(self) -> None:
        manager = LLMManager()
        assert manager is not None
        assert manager.registry is not None
        assert manager.factory is not None
        assert manager.metrics is not None

    @pytest.mark.asyncio
    async def test_health_check_empty(self) -> None:
        manager = LLMManager()
        health = await manager.health_check()
        assert health["healthy"] is False
        assert health["provider_count"] == 0


# =========================================================================
# OpenAI-specific (mocked)
# =========================================================================


class TestOpenAIProviderMocked:
    @pytest.mark.asyncio
    async def test_generate_success(self) -> None:
        """Test that generate returns properly structured response."""
        from ..providers.openai_provider import OpenAIProvider

        p = OpenAIProvider(api_key="sk-test")
        # Patch the client to avoid real API calls
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.id = "chatcmpl-test"
        mock_response.model = "gpt-4o"
        mock_choice = AsyncMock()
        mock_choice.index = 0
        mock_choice.finish_reason = "stop"
        mock_message = AsyncMock()
        mock_message.content = "Hello! How can I help you?"
        mock_message.tool_calls = None
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_usage = AsyncMock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_usage.total_tokens = 30
        mock_response.usage = mock_usage
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Use the executor to bypass _get_client
        original_get_client = p._get_client
        p._get_client = lambda: mock_client

        result = await p.generate("Hello")
        assert result["success"] is True
        assert "help" in result["content"].lower()
        assert result["tokens_prompt"] == 10
        assert result["tokens_completion"] == 20

        # Restore
        p._get_client = original_get_client


# =========================================================================
# Anthropic-specific (mocked)
# =========================================================================


class TestAnthropicProviderMocked:
    @pytest.mark.asyncio
    async def test_generate_success(self) -> None:
        """Test that generate returns properly structured response."""
        from ..providers.anthropic_provider import AnthropicProvider

        p = AnthropicProvider(api_key="sk-ant-test")
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.id = "msg_test"
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.stop_reason = "end_turn"
        mock_block = AsyncMock()
        mock_block.type = "text"
        mock_block.text = "I'm Claude, nice to meet you!"
        mock_response.content = [mock_block]
        mock_usage = AsyncMock()
        mock_usage.input_tokens = 15
        mock_usage.output_tokens = 25
        mock_response.usage = mock_usage
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        original_get_client = p._get_client
        p._get_client = lambda: mock_client

        result = await p.generate("Hello")
        assert result["success"] is True
        assert "Claude" in result["content"]
        assert result["tokens_prompt"] == 15
        assert result["tokens_completion"] == 25

        p._get_client = original_get_client


# =========================================================================
# DeepSeek-specific (mocked)
# =========================================================================


class TestDeepSeekProviderMocked:
    @pytest.mark.asyncio
    async def test_generate_success(self) -> None:
        """Test that generate returns properly structured response."""
        from ..providers.deepseek_provider import DeepSeekProvider

        p = DeepSeekProvider(api_key="sk-ds-test")
        mock_client = AsyncMock()

        class FakeResponse:
            status_code = 200

            def json(self):
                return {
                    "id": "ds-test",
                    "model": "deepseek-chat",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"content": "DeepSeek response here!", "role": "assistant"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 20, "completion_tokens": 30, "total_tokens": 50},
                }

        mock_client.post = AsyncMock(return_value=FakeResponse())

        original_get_client = p._get_client
        p._get_client = lambda: mock_client

        result = await p.generate("Hello")
        assert result["success"] is True
        assert "DeepSeek" in result["content"]
        assert result["tokens_prompt"] == 20

        p._get_client = original_get_client
