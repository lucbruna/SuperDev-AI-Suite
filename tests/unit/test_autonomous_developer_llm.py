"""Tests for the deterministic LLM facade (Phase F)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.config.llm_config import LLMConfig
from modules.autonomous_developer.core.exceptions import ExecutionError
from modules.autonomous_developer.llm import LLMClient, LLMError, estimate_tokens


class TestEstimateTokens:
    def test_empty_text(self):
        assert estimate_tokens("") == 0

    def test_single_token(self):
        assert estimate_tokens("abcd") == 1

    def test_two_tokens(self):
        assert estimate_tokens("abcde") == 2

    def test_long_text(self):
        assert estimate_tokens("x" * 100) == 25


class TestLLMClient:
    def test_mock_response_verbatim(self):
        response = LLMClient(mock_response="fixed").complete("anything")
        assert response.text == "fixed"
        assert response.provider == "local"
        assert response.model == ""

    def test_mock_usage_counts(self):
        response = LLMClient(mock_response="fixed").complete("hello world")
        assert response.usage["prompt_tokens"] == 3  # 11 chars -> 3 tokens
        assert response.usage["completion_tokens"] == estimate_tokens("fixed")

    def test_echo_fallback(self):
        response = LLMClient().complete("Hello\nWorld")
        assert response.text == "Echo: Hello"

    def test_echo_empty_prompt(self):
        assert LLMClient().complete("").text == "Echo: <empty prompt>"

    def test_max_tokens_truncates(self):
        client = LLMClient(mock_response="x" * 100)
        response = client.complete("p", max_tokens=2)
        assert len(response.text) == 8
        assert response.usage["completion_tokens"] == 2

    def test_fallback_disabled_raises(self):
        client = LLMClient(config=LLMConfig(fallback_to_echo=False))
        with pytest.raises(LLMError):
            client.complete("hi")

    def test_llm_error_is_execution_error(self):
        assert issubclass(LLMError, ExecutionError)

    def test_custom_model(self):
        client = LLMClient(config=LLMConfig(model="gpt-test"))
        assert client.complete("hi").model == "gpt-test"

    def test_response_dataclass(self):
        response = LLMClient(mock_response="ok").complete("hi")
        assert response.usage == {"prompt_tokens": 1, "completion_tokens": 1}
        assert response.text == "ok"
