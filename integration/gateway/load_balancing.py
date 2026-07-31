from __future__ import annotations

import itertools
import logging
from typing import Any


class LoadBalancer:
    """Round-robin load balancer over a pool of targets."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.gateway.load_balancing")
        self._targets: list[str] = []
        self._cursor = itertools.count(0)

    def add_target(self, target: str) -> None:
        if target not in self._targets:
            self._targets.append(target)

    def remove_target(self, target: str) -> bool:
        try:
            self._targets.remove(target)
            return True
        except ValueError:
            return False

    def next(self) -> str | None:
        if not self._targets:
            return None
        index = next(self._cursor) % len(self._targets)
        return self._targets[index]

    def list_targets(self) -> list[str]:
        return list(self._targets)

    def count(self) -> int:
        return len(self._targets)
