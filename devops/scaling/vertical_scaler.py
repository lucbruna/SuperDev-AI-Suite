from __future__ import annotations

import logging
from typing import Any


class VerticalScaler:
    """Adjusts resource allocations (CPU, memory) of workloads."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.scaling.vertical")

    def recommend(self, service: str) -> dict[str, Any]:
        raise NotImplementedError

    def apply(self, service: str, cpu: str | None = None, memory: str | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def history(self, service: str) -> list[dict[str, Any]]:
        raise NotImplementedError
