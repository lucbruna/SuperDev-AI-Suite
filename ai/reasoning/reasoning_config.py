from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReasoningConfig:
    """Configuration for the reasoning engine."""

    max_hypotheses: int = 5
    confidence_threshold: float = 0.5
    max_reasoning_depth: int = 10
    timeout_seconds: int = 60
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    memory_enabled: bool = True
    profiler_enabled: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_hypotheses": self.max_hypotheses,
            "confidence_threshold": self.confidence_threshold,
            "max_reasoning_depth": self.max_reasoning_depth,
            "timeout_seconds": self.timeout_seconds,
            "cache_enabled": self.cache_enabled,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "memory_enabled": self.memory_enabled,
            "profiler_enabled": self.profiler_enabled,
        }
