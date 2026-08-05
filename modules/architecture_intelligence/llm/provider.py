"""LLM provider abstraction with graceful degradation.

Supports OpenAI-compatible chat-completions endpoints (OpenAI, local servers
like Ollama/LM Studio, proxies) plus Anthropic. When no provider is
configured or reachable, ``available`` is False and callers fall back to
heuristic paths. Uses only the standard library (urllib) to avoid a hard
dependency.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)


class LLMProvider:
    """Minimal OpenAI/Anthropic-compatible chat client."""

    def __init__(self, config: Any | None = None) -> None:
        from modules.architecture_intelligence.config.intelligence_settings import (
            get_settings,
        )

        self.config = (config or get_settings().config)
        self._provider = self.config.llm_provider.lower()
        self._model = self.config.llm_model
        self._api_key = self.config.llm_api_key or os.getenv("OPENAI_API_KEY", "")
        self._base_url = (self.config.llm_base_url or os.getenv("OPENAI_BASE_URL", "")).rstrip("/")
        self._timeout = self.config.llm_timeout_seconds

    @property
    def available(self) -> bool:
        return self._provider not in {"", "none", "auto"} and bool(self._api_key or self._base_url)

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 512) -> str:
        """Run a chat completion; raises on transport errors."""
        if not self.available:
            raise RuntimeError("No LLM provider configured")
        if self._provider == "anthropic" and self._api_key:
            return self._complete_anthropic(prompt, system, max_tokens)
        return self._complete_openai(prompt, system, max_tokens)

    # ---------------------------------------------------------------- openai
    def _complete_openai(self, prompt: str, system: str | None, max_tokens: int) -> str:
        base = self._base_url or "https://api.openai.com/v1"
        url = f"{base}/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self._model or "gpt-4o-mini",
            "messages": messages,
            "max_tokens": max_tokens,
        }
        data = self._post_json(url, payload)
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            raise RuntimeError(f"Unexpected OpenAI response: {str(data)[:200]}")

    # ------------------------------------------------------------- anthropic
    def _complete_anthropic(self, prompt: str, system: str | None, max_tokens: int) -> str:
        url = "https://api.anthropic.com/v1/messages"
        payload: dict[str, Any] = {
            "model": self._model or "claude-3-5-sonnet-latest",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system
        data = self._post_json(
            url, payload, headers={"x-api-key": self._api_key, "anthropic-version": "2023-06-01"}
        )
        try:
            return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
        except Exception:
            raise RuntimeError(f"Unexpected Anthropic response: {str(data)[:200]}")

    # ---------------------------------------------------------------- transport
    def _post_json(self, url: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
        request_headers: dict[str, str] = {
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}),
            **(headers or {}),
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=request_headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self._timeout) as response:
            body = response.read().decode("utf-8")
        return json.loads(body)


_provider: LLMProvider | None = None
_lock = threading.Lock()


def get_provider() -> LLMProvider:
    """Process-wide singleton provider (lazy)."""
    global _provider
    if _provider is None:
        with _lock:
            if _provider is None:
                _provider = LLMProvider()
    return _provider


def complete(prompt: str, **kwargs: Any) -> str | None:
    """Best-effort completion; returns None when no provider is available."""
    try:
        provider = get_provider()
        if not provider.available:
            return None
        return provider.complete(prompt, **kwargs)
    except Exception as exc:
        logger.debug("LLM completion failed: %s", exc)
        return None
