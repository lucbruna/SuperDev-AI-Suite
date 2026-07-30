from __future__ import annotations

import hashlib
import random
from abc import ABC, abstractmethod


class Sampler(ABC):
    """Abstract base for trace sampling strategies."""

    @abstractmethod
    def should_sample(self, trace_id: str, operation_name: str = "") -> bool: ...


class AlwaysOnSampler(Sampler):
    """Samples every trace."""

    def should_sample(self, trace_id: str, operation_name: str = "") -> bool:
        return True


class AlwaysOffSampler(Sampler):
    """Samples no traces."""

    def should_sample(self, trace_id: str, operation_name: str = "") -> bool:
        return False


class RateSampler(Sampler):
    """Samples traces at a given rate (0.0 to 1.0)."""

    def __init__(self, rate: float = 1.0) -> None:
        self._rate = max(0.0, min(1.0, rate))

    def should_sample(self, trace_id: str, operation_name: str = "") -> bool:
        return random.random() < self._rate


class DeterministicSampler(Sampler):
    """Deterministic sampling based on trace_id hash."""

    def __init__(self, rate: float = 1.0) -> None:
        self._rate = max(0.0, min(1.0, rate))
        self._threshold = int(self._rate * 0xFFFFFFFF)

    def should_sample(self, trace_id: str, operation_name: str = "") -> bool:
        hash_val = int(hashlib.md5(trace_id.encode()).hexdigest()[:8], 16)
        return hash_val < self._threshold


class OperationBasedSampler(Sampler):
    """Samples based on operation name patterns."""

    def __init__(
        self,
        always_sample: set[str] | None = None,
        never_sample: set[str] | None = None,
        default_rate: float = 0.1,
    ) -> None:
        self._always = always_sample or set()
        self._never = never_sample or set()
        self._fallback = RateSampler(default_rate)

    def should_sample(self, trace_id: str, operation_name: str = "") -> bool:
        if operation_name in self._always:
            return True
        if operation_name in self._never:
            return False
        return self._fallback.should_sample(trace_id, operation_name)
