"""Live LLM provider calls — OpenAI, Ollama, Gemini and Claude.

Every call goes through :mod:`httpx` so the transport can be swapped in
tests (``httpx.MockTransport``) to keep provider tests offline and
deterministic. All network errors, HTTP errors and malformed payloads are
normalized to :class:`LLMError`; secrets (API keys) never appear in error
messages or logs.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from modules.autonomous_developer.config.llm_config import LLMConfig
from modules.autonomous_developer.llm.errors import LLMError

__all__ = ["ProviderResult", "is_configured", "complete"]

_ANTHROPIC_VERSION = "2023-06-01"


@dataclass(slots=True)
class ProviderResult:
    """Parsed output of a live provider call."""

    text: str
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)


def is_configured(config: LLMConfig) -> bool:
    """Whether ``config.provider`` has everything needed for a live call."""
    provider = (config.provider or "local").lower()
    if provider == "local":
        return False
    if provider in {"openai", "gemini", "claude"}:
        key = getattr(config, f"{provider}_api_key", "")
        return bool(key.strip())
    if provider == "ollama":
        return bool(config.ollama_url.strip())
    return False


def _model_for(config: LLMConfig, provider: str) -> str:
    if config.model and config.model.strip():
        return config.model.strip()
    return getattr(config, f"{provider}_model", "").strip() or provider


def _post_with_retry(
    client: httpx.Client,
    url: str,
    *,
    headers: dict[str, str],
    json_body: dict[str, Any],
    max_retries: int,
) -> httpx.Response:
    """POST with retry/backoff on transport errors and 5xx; 4xx raises."""
    attempt = 0
    while True:
        try:
            response = client.post(url, headers=headers, json=json_body)
        except httpx.HTTPError as exc:
            if attempt >= max_retries:
                raise LLMError(f"Network error calling provider: {exc.__class__.__name__}") from exc
            attempt += 1
            time.sleep(0.5 * attempt)
            continue
        if response.status_code >= 500 and attempt < max_retries:
            attempt += 1
            time.sleep(0.5 * attempt)
            continue
        if response.status_code >= 400:
            raise LLMError(
                f"Provider HTTP {response.status_code}: "
                f"{response.text[:300] if response.text else 'no body'}"
            )
        return response


def _call_openai(
    config: LLMConfig, prompt: str, max_tokens: int, client: httpx.Client
) -> ProviderResult:
    model = _model_for(config, "openai")
    url = config.openai_base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.openai_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": config.temperature,
    }
    response = _post_with_retry(
        client, url, headers=headers, json_body=body, max_retries=config.max_retries
    )
    payload = response.json()
    try:
        text = payload["choices"][0]["message"]["content"] or ""
        usage = {
            "prompt_tokens": payload.get("usage", {}).get("prompt_tokens", 0) or 0,
            "completion_tokens": payload.get("usage", {}).get("completion_tokens", 0) or 0,
        }
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Malformed OpenAI response payload") from exc
    return ProviderResult(text=text, model=model, usage=usage)


def _call_ollama(
    config: LLMConfig, prompt: str, max_tokens: int, client: httpx.Client
) -> ProviderResult:
    model = _model_for(config, "ollama")
    url = config.ollama_url.rstrip("/") + "/api/chat"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": config.temperature, "num_predict": max_tokens},
    }
    response = _post_with_retry(
        client, url, headers={"Content-Type": "application/json"}, json_body=body,
        max_retries=config.max_retries,
    )
    payload = response.json()
    try:
        text = payload["message"]["content"] or ""
        usage = {
            "prompt_tokens": payload.get("prompt_eval_count", 0) or 0,
            "completion_tokens": payload.get("eval_count", 0) or 0,
        }
    except (KeyError, TypeError) as exc:
        raise LLMError("Malformed Ollama response payload") from exc
    return ProviderResult(text=text, model=model, usage=usage)


def _call_gemini(
    config: LLMConfig, prompt: str, max_tokens: int, client: httpx.Client
) -> ProviderResult:
    model = _model_for(config, "gemini")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
        f":generateContent?key={config.gemini_api_key}"
    )
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": config.temperature,
        },
    }
    response = _post_with_retry(
        client, url, headers={"Content-Type": "application/json"}, json_body=body,
        max_retries=config.max_retries,
    )
    payload = response.json()
    try:
        text = payload["candidates"][0]["content"]["parts"][0]["text"] or ""
        meta = payload.get("usageMetadata", {}) or {}
        usage = {
            "prompt_tokens": meta.get("promptTokenCount", 0) or 0,
            "completion_tokens": meta.get("candidatesTokenCount", 0) or 0,
        }
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Malformed Gemini response payload") from exc
    return ProviderResult(text=text, model=model, usage=usage)


def _call_claude(
    config: LLMConfig, prompt: str, max_tokens: int, client: httpx.Client
) -> ProviderResult:
    model = _model_for(config, "claude")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": config.claude_api_key,
        "anthropic-version": _ANTHROPIC_VERSION,
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": config.temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    response = _post_with_retry(
        client, url, headers=headers, json_body=body, max_retries=config.max_retries
    )
    payload = response.json()
    try:
        text = payload["content"][0]["text"] or ""
        usage = {
            "prompt_tokens": payload.get("usage", {}).get("input_tokens", 0) or 0,
            "completion_tokens": payload.get("usage", {}).get("output_tokens", 0) or 0,
        }
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Malformed Claude response payload") from exc
    return ProviderResult(text=text, model=model, usage=usage)


def complete(
    config: LLMConfig,
    prompt: str,
    *,
    max_tokens: int | None = None,
    transport: httpx.BaseTransport | None = None,
) -> ProviderResult:
    """Call the configured live provider; raises :class:`LLMError` on failure."""
    provider = (config.provider or "local").lower()
    if not is_configured(config):
        raise LLMError(f"Provider {config.provider!r} is not configured")
    token_budget = max_tokens or config.max_tokens
    with httpx.Client(transport=transport, timeout=config.timeout_seconds) as client:
        if provider == "openai":
            return _call_openai(config, prompt, token_budget, client)
        if provider == "ollama":
            return _call_ollama(config, prompt, token_budget, client)
        if provider == "gemini":
            return _call_gemini(config, prompt, token_budget, client)
        if provider == "claude":
            return _call_claude(config, prompt, token_budget, client)
        raise LLMError(f"Unknown provider {config.provider!r}")
