from __future__ import annotations

import pytest

from ..providers.mock_provider import MockProvider
from ..providers.openai_provider import OpenAIProvider
from ..providers.anthropic_provider import AnthropicProvider
from ..providers.base_provider import BaseLLMProvider


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


class TestOpenAIProvider:
    @pytest.mark.asyncio
    async def test_generate(self) -> None:
        p = OpenAIProvider(api_key="test-key")
        result = await p.generate("Hello")
        assert result["success"] is True
        assert "OpenAI" in result["content"]

    @pytest.mark.asyncio
    async def test_validate(self) -> None:
        p = OpenAIProvider()
        assert await p.validate({"max_tokens": 100}) is True

    def test_to_dict(self) -> None:
        p = OpenAIProvider(api_key="sk-123")
        d = p.to_dict()
        assert d["api_key_set"] is True


class TestAnthropicProvider:
    @pytest.mark.asyncio
    async def test_generate(self) -> None:
        p = AnthropicProvider()
        result = await p.generate("Hello")
        assert "Anthropic" in result["content"]


class TestBaseProvider:
    @pytest.mark.asyncio
    async def test_ensure_deterministic(self) -> None:
        p = MockProvider()
        kwargs = p._ensure_deterministic({"temperature": 0.7})
        assert kwargs["temperature"] == 0.0
