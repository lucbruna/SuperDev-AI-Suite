from __future__ import annotations

import itertools
from enum import StrEnum

from ..providers.base_provider import BaseProvider


class LoadBalanceStrategy(StrEnum):
    ROUND_ROBIN = "round_robin"
    LEAST_LATENCY = "least_latency"
    LEAST_COST = "least_cost"


class LoadBalancer:
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self._round_robin = itertools.cycle([])
        self._providers: list[BaseProvider] = []
        self._latency_map: dict[str, float] = {}

    def set_providers(self, providers: list[BaseProvider]) -> None:
        self._providers = providers
        self._round_robin = itertools.cycle(providers)

    def record_latency(self, name: str, latency_ms: float) -> None:
        self._latency_map[name] = latency_ms

    def get_next_provider(self, capability: str = "") -> BaseProvider | None:
        if not self._providers:
            return None

        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return next(self._round_robin)

        if self.strategy == LoadBalanceStrategy.LEAST_LATENCY:
            best = min(
                self._providers,
                key=lambda p: self._latency_map.get(getattr(p.config, 'name', str(id(p))), float("inf")),
            )
            return best

        if self.strategy == LoadBalanceStrategy.LEAST_COST:
            return self._providers[0] if self._providers else None

        return self._providers[0] if self._providers else None
