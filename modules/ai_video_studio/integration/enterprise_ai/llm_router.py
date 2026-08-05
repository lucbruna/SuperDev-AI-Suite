"""LLM Router — routes prompts to the best configured provider."""
from __future__ import annotations

from typing import Any

#: Provider registry with capability metadata (no network calls).
_PROVIDERS: dict[str, dict[str, Any]] = {
    "openai": {"models": ("gpt-4o", "gpt-4o-mini"), "multilingual": True, "reasoning": True},
    "anthropic": {"models": ("claude-3-7-sonnet", "claude-3-5-haiku"), "multilingual": True, "reasoning": True},
    "local": {"models": ("formant-1", "studio-lite"), "multilingual": False, "reasoning": False},
}

_ROUTING_HINTS: dict[str, str] = {
    "script": "openai", "storyboard": "anthropic", "translation": "openai",
    "subtitles": "local", "voice": "local", "reasoning": "anthropic",
}


class LLMRouter:
    """Deterministic provider selection with capability metadata."""

    def __init__(self) -> None:
        self._preferred = "openai"

    def providers(self) -> list[dict[str, Any]]:
        return [{"name": n, **meta} for n, meta in _PROVIDERS.items()]

    def route(self, prompt: str, *, task: str | None = None,
              provider: str | None = None) -> dict[str, Any]:
        """Pick a provider/model for *prompt* (fallback chain included)."""
        chosen = provider or _ROUTING_HINTS.get(task or "", self._preferred)
        if chosen not in _PROVIDERS:
            chosen = self._preferred
        meta = _PROVIDERS[chosen]
        return {
            "provider": chosen,
            "model": meta["models"][0],
            "task": task or "general",
            "reasoning": meta["reasoning"],
            "multilingual": meta["multilingual"],
            "prompt_tokens": max(1, len(prompt.split())),
        }


_llm_router: LLMRouter | None = None


def get_llm_router() -> LLMRouter:
    global _llm_router
    if _llm_router is None:
        _llm_router = LLMRouter()
    return _llm_router
