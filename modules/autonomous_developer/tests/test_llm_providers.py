"""Offline tests for live LLM providers (mock transport, no network)."""
from __future__ import annotations

from typing import Any

import httpx
import pytest

from modules.autonomous_developer.config.llm_config import LLMConfig
from modules.autonomous_developer.llm.client import LLMClient, LLMError


def _handler(
    payload: dict, status: int = 200
) -> tuple[Any, dict[str, httpx.Request]]:
    captured: dict[str, httpx.Request] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return httpx.Response(status, json=payload, request=request)

    return handler, captured


def _client(
    *,
    provider: str = "openai",
    enabled: bool = True,
    api_key: str = "sk-test",
    base_url: str = "https://api.openai.com/v1",
    transport: httpx.BaseTransport | None = None,
    mock: str | None = None,
) -> LLMClient:
    cfg = LLMConfig(
        enabled=enabled,
        provider=provider,
        openai_api_key=api_key,
        openai_base_url=base_url,
        gemini_api_key=api_key,
        claude_api_key=api_key,
        ollama_url="http://localhost:11434",
    )
    return LLMClient(cfg, mock_response=mock, transport=transport)


class TestOpenAI:
    def test_route_and_parse(self):
        handler, captured = _handler(
            {
                "choices": [{"message": {"content": "openai answer"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 3},
            }
        )
        client = _client(transport=httpx.MockTransport(handler))
        result = client.complete("hello")
        assert result.text == "openai answer"
        assert result.provider == "openai"
        assert result.usage == {"prompt_tokens": 12, "completion_tokens": 3}
        request = captured["request"]
        assert request.url == "https://api.openai.com/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer sk-test"
        body = request.read().decode()
        assert '"gpt-4o-mini"' in body
        assert '"max_tokens"' in body

    def test_custom_base_url(self):
        handler, captured = _handler({"choices": [{"message": {"content": "ok"}}]})
        client = _client(
            base_url="http://localhost:9000/v1", transport=httpx.MockTransport(handler)
        )
        client.complete("hi")
        assert captured["request"].url == "http://localhost:9000/v1/chat/completions"

    def test_retries_then_succeeds_on_500(self):
        calls = {"n": 0}

        def flaky(request: httpx.Request) -> httpx.Response:
            calls["n"] += 1
            if calls["n"] < 3:
                return httpx.Response(500, json={"error": "boom"}, request=request)
            return httpx.Response(
                200, json={"choices": [{"message": {"content": "after retry"}}]},
                request=request,
            )

        client = _client(transport=httpx.MockTransport(flaky))
        assert client.complete("x").text == "after retry"
        assert calls["n"] == 3

    def test_http_400_raises_immediately(self):
        handler, _ = _handler({"error": {"message": "invalid api key"}}, status=401)
        client = _client(transport=httpx.MockTransport(handler))
        with pytest.raises(LLMError, match="401"):
            client.complete("x")


class TestOllama:
    def test_route_and_parse(self):
        handler, captured = _handler(
            {"message": {"content": "ollama answer"}, "prompt_eval_count": 9,
             "eval_count": 4}
        )
        client = _client(
            provider="ollama", transport=httpx.MockTransport(handler)
        )
        result = client.complete("hello")
        assert result.text == "ollama answer"
        assert result.provider == "ollama"
        assert result.usage == {"prompt_tokens": 9, "completion_tokens": 4}
        request = captured["request"]
        assert request.url == "http://localhost:11434/api/chat"
        body = request.read().decode()
        assert '"llama3"' in body
        assert '"stream":false' in body


class TestGemini:
    def test_route_and_parse(self):
        handler, captured = _handler(
            {
                "candidates": [{"content": {"parts": [{"text": "gemini answer"}]}}],
                "usageMetadata": {"promptTokenCount": 5,
                                  "candidatesTokenCount": 2},
            }
        )
        client = _client(
            provider="gemini", transport=httpx.MockTransport(handler)
        )
        result = client.complete("hello")
        assert result.text == "gemini answer"
        assert result.provider == "gemini"
        assert result.usage == {"prompt_tokens": 5, "completion_tokens": 2}
        request = captured["request"]
        url = str(request.url)
        assert "generateContent" in url
        assert "key=sk-test" in url


class TestClaude:
    def test_route_and_parse(self):
        handler, captured = _handler(
            {
                "content": [{"type": "text", "text": "claude answer"}],
                "usage": {"input_tokens": 7, "output_tokens": 3},
            }
        )
        client = _client(
            provider="claude", transport=httpx.MockTransport(handler)
        )
        result = client.complete("hello")
        assert result.text == "claude answer"
        assert result.provider == "claude"
        assert result.usage == {"prompt_tokens": 7, "completion_tokens": 3}
        request = captured["request"]
        assert request.url == "https://api.anthropic.com/v1/messages"
        assert request.headers["x-api-key"] == "sk-test"
        assert request.headers["anthropic-version"] == "2023-06-01"


class TestResolution:
    def test_mock_wins_over_provider(self):
        handler, _ = _handler({"choices": [{"message": {"content": "live"}}]})
        client = _client(transport=httpx.MockTransport(handler), mock="canned")
        assert client.complete("x").text == "canned"

    def test_disabled_falls_back_to_echo(self):
        handler, _ = _handler({})
        client = _client(enabled=False, transport=httpx.MockTransport(handler))
        result = client.complete("hi there")
        assert result.text == "Echo: hi there"
        assert result.provider == "local"

    def test_enabled_missing_key_falls_back_to_echo(self):
        client = _client(api_key="")
        assert client.complete("hello").text == "Echo: hello"

    def test_enabled_no_fallback_raises(self):
        cfg = LLMConfig(enabled=True, provider="openai", fallback_to_echo=False)
        with pytest.raises(LLMError, match="No live provider configured"):
            LLMClient(cfg).complete("x")

    def test_provider_local_is_never_live(self):
        cfg = LLMConfig(enabled=True, provider="local", fallback_to_echo=False)
        with pytest.raises(LLMError):
            LLMClient(cfg).complete("x")

    def test_malformed_provider_response_raises(self):
        handler, _ = _handler({"unexpected": True})
        client = _client(transport=httpx.MockTransport(handler))
        with pytest.raises(LLMError, match="Malformed"):
            client.complete("x")

    def test_network_error_normalized(self):
        def boom(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("refused", request=request)

        client = _client(transport=httpx.MockTransport(boom))
        with pytest.raises(LLMError, match="Network error"):
            client.complete("x")
