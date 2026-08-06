"""Deterministic, network-safe LLM facade.

The client defaults to a fully offline backend for pipelines and tests:
a ``mock_response`` short-circuits every completion with the same text, and
without a mock it returns a canned echo-style completion when
``config.fallback_to_echo`` is enabled. When ``config.enabled`` is set and
the configured provider has its credentials, ``complete`` routes to the live
provider (OpenAI, Ollama, Gemini or Claude) via :mod:`providers`. Every
network failure is normalized to :class:`LLMError`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from modules.autonomous_developer.config.llm_config import LLMConfig
from modules.autonomous_developer.llm import providers
from modules.autonomous_developer.llm.errors import LLMError

__all__ = ["LLMClient", "LLMError", "LLMResponse", "estimate_tokens"]


def estimate_tokens(text: str) -> int:
    """Heuristic token count: ~4 characters per token, at least 1."""
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


@dataclass(slots=True)
class LLMResponse:
    """The result of a completed LLM call."""

    text: str
    model: str = ""
    provider: str = "local"
    usage: dict[str, int] = field(default_factory=dict)


class LLMClient:
    """Calls LLM backends deterministically, defaulting to a local echo.

    Parameters
    ----------
    config:
        LLM settings; a default :class:`LLMConfig` is used when omitted.
    mock_response:
        When set, every ``complete`` returns this text verbatim, making the
        client fully deterministic regardless of configuration.
    """

    def __init__(
        self,
        config: LLMConfig | None = None,
        mock_response: str | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.config = config or LLMConfig()
        self.mock_response = mock_response
        self.transport = transport

    def complete(
        self, prompt: str, *, max_tokens: int | None = None
    ) -> LLMResponse:
        """Produce a completion for ``prompt``.

        Resolution order: mock response, live provider (when enabled and
        configured), echo fallback, then :class:`LLMError`.
        """
        if self.mock_response is not None:
            text = self.mock_response
            model = self.config.model
            provider = "local"
            usage: dict[str, int] = {}
        elif self.config.enabled and providers.is_configured(self.config):
            result = providers.complete(
                self.config,
                prompt,
                max_tokens=max_tokens,
                transport=self.transport,
            )
            text = result.text
            model = result.model
            provider = self.config.provider
            usage = result.usage
        elif self.config.fallback_to_echo:
            first_line = next(
                (line.strip() for line in prompt.splitlines() if line.strip()),
                "",
            )
            text = f"Echo: {first_line}" if first_line else "Echo: <empty prompt>"
            model = self.config.model
            provider = "local"
            usage = {
                "prompt_tokens": estimate_tokens(prompt),
                "completion_tokens": estimate_tokens(text),
            }
        else:
            raise LLMError(
                f"No live provider configured (provider={self.config.provider!r})"
            )

        if max_tokens is not None:
            max_chars = max(1, max_tokens * 4)
            if len(text) > max_chars:
                text = text[:max_chars]

        if not usage:
            usage = {
                "prompt_tokens": estimate_tokens(prompt),
                "completion_tokens": estimate_tokens(text),
            }
        return LLMResponse(text=text, model=model, provider=provider, usage=usage)
