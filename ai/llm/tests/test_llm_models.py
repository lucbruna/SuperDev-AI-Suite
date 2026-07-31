from __future__ import annotations

from ..llm_models import LLMContext, LLMMetrics, LLMRequest, LLMResponse, ProviderInfo, ProviderState, TokenUsage


class TestLLMRequest:
    def test_defaults(self) -> None:
        req = LLMRequest(provider="openai", model="gpt-4", prompt="Hello")
        assert req.provider == "openai"
        assert req.model == "gpt-4"
        assert req.prompt == "Hello"
        assert req.max_tokens == 1024
        assert req.temperature == 0.7

    def test_custom_params(self) -> None:
        req = LLMRequest(
            provider="anthropic",
            model="claude-3",
            prompt="Test",
            max_tokens=512,
            temperature=0.5,
        )
        assert req.max_tokens == 512
        assert req.temperature == 0.5


class TestLLMResponse:
    def test_defaults(self) -> None:
        resp = LLMResponse(request_id="r1", provider="openai", model="gpt-4", content="Hi")
        assert resp.content == "Hi"
        assert resp.finish_reason == "stop"
        assert resp.tokens_prompt == 0

    def test_full_response(self) -> None:
        resp = LLMResponse(
            request_id="r2",
            provider="anthropic",
            model="claude-3",
            content="Hello world",
            tokens_prompt=10,
            tokens_completion=20,
            latency_ms=150.0,
            cost_usd=0.001,
            finish_reason="stop",
        )
        assert resp.tokens_prompt == 10
        assert resp.latency_ms == 150.0


class TestProviderInfo:
    def test_defaults(self) -> None:
        info = ProviderInfo(name="openai", model="gpt-4")
        assert info.state == ProviderState.ACTIVE
        assert info.capabilities == []
        assert info.supports_streaming is True

    def test_custom(self) -> None:
        info = ProviderInfo(
            name="test",
            model="m",
            state=ProviderState.ERROR,
            capabilities=["chat", "vision"],
            cost_per_token=0.01,
        )
        assert info.state == ProviderState.ERROR
        assert "vision" in info.capabilities


class TestTokenUsage:
    def test_defaults(self) -> None:
        tu = TokenUsage()
        assert tu.total_tokens == 0

    def test_custom(self) -> None:
        tu = TokenUsage(prompt_tokens=100, completion_tokens=50, cost_usd=0.002)
        assert tu.total_tokens == 150


class TestLLMMetrics:
    def test_defaults(self) -> None:
        m = LLMMetrics()
        assert m.success is False

    def test_record(self) -> None:
        m = LLMMetrics(provider="o", model="gpt-4", latency_ms=200, success=True)
        assert m.latency_ms == 200.0


class TestLLMContext:
    def test_defaults(self) -> None:
        ctx = LLMContext(request_id="r1")
        assert ctx.user_id == ""
        assert ctx.permissions == []
