"""LLMRegistry — deterministic provider registry.

Providers are static metadata (name, capabilities, quality, cost). Selection
is a pure function of the required capabilities and the preference:
- default: highest ``quality``, ties broken by lower ``cost`` then name.
- ``prefer='cheap'``: lowest ``cost``, ties by quality then name.
- ``prefer='local'``: any provider with the ``local`` capability, highest
  quality first.

No API calls happen here; this is the decision surface used by the
Decision Engine. Runtime invocation is delegated to integrations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

# Canonical capability vocabulary.
CODING = "coding"
REASONING = "reasoning"
ANALYSIS = "analysis"
PLANNING = "planning"
OPERATIONS = "operations"
VISION = "vision"
FAST = "fast"
CHEAP = "cheap"
LOCAL = "local"

_CAPABILITIES: set[str] = {
    CODING,
    REASONING,
    ANALYSIS,
    PLANNING,
    OPERATIONS,
    VISION,
    FAST,
    CHEAP,
    LOCAL,
}


@dataclass(frozen=True, slots=True)
class LLMProvider:
    """Static description of an LLM provider.

    Attributes:
        name: provider id (e.g. ``openai``).
        display: human-friendly label.
        capabilities: what the provider can do.
        quality: 0..1 quality score used as the default tiebreaker.
        cost: cost per 1K tokens (informational, drives 'cheap' preference).
    """

    name: str
    display: str
    capabilities: frozenset[str]
    quality: float
    cost: float

    def supports(self, required: set[str]) -> bool:
        return required <= self.capabilities

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["capabilities"] = sorted(self.capabilities)
        return data


# Default provider catalogue (deterministic, static metadata).
def default_providers() -> tuple[LLMProvider, ...]:
    return (
        LLMProvider("openai", "OpenAI", frozenset({CODING, REASONING, ANALYSIS, PLANNING, OPERATIONS, VISION}), 0.90, 0.020),
        LLMProvider("claude", "Claude", frozenset({CODING, REASONING, ANALYSIS, PLANNING, OPERATIONS, VISION}), 0.95, 0.015),
        LLMProvider("gemini", "Gemini", frozenset({CODING, REASONING, ANALYSIS, PLANNING, OPERATIONS, VISION, FAST}), 0.85, 0.010),
        LLMProvider("deepseek", "DeepSeek", frozenset({CODING, REASONING, ANALYSIS, CHEAP}), 0.80, 0.001),
        LLMProvider("mistral", "Mistral", frozenset({CODING, REASONING, ANALYSIS, CHEAP, FAST}), 0.75, 0.002),
        LLMProvider("ollama", "Ollama", frozenset({CODING, REASONING, ANALYSIS, OPERATIONS, LOCAL}), 0.70, 0.0),
        LLMProvider("llama", "Llama", frozenset({CODING, ANALYSIS, OPERATIONS, LOCAL}), 0.65, 0.0),
    )


class LLMRegistry:
    """Provider catalogue with deterministic selection.

    Attributes:
        providers: name -> provider.
    """

    def __init__(self, providers: tuple[LLMProvider, ...] | None = None) -> None:
        catalogue = providers if providers is not None else default_providers()
        self.providers: dict[str, LLMProvider] = {p.name: p for p in catalogue}

    def get(self, name: str) -> LLMProvider | None:
        return self.providers.get(name)

    def all(self) -> tuple[LLMProvider, ...]:
        return tuple(self.providers.values())

    def select(
        self,
        required: set[str],
        prefer: str | None = None,
    ) -> str:
        """Pick a provider id for the required capabilities.

        Raises:
            ValueError: if no provider supports the required capabilities.
        """
        candidates = [p for p in self.providers.values() if p.supports(required)]
        if not candidates:
            raise ValueError(
                f"no provider supports capabilities {sorted(required)}"
            )
        if prefer == "local":
            candidates = [p for p in candidates if LOCAL in p.capabilities]
            if not candidates:
                raise ValueError("no local provider supports the capabilities")
            return min(candidates, key=lambda p: (-p.quality, p.name)).name
        if prefer == "cheap":
            return min(candidates, key=lambda p: (p.cost, -p.quality, p.name)).name
        # Default: highest quality, then lowest cost, then name.
        return min(candidates, key=lambda p: (-p.quality, p.cost, p.name)).name

    def to_dict(self) -> dict[str, Any]:
        return {"providers": [p.to_dict() for p in self.all()]}
