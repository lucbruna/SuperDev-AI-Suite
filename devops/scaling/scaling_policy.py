from __future__ import annotations

import logging
from typing import Any


class ScalingPolicy:
    """Defines autoscaling policies."""

    def __init__(self, name: str, metric: str) -> None:
        self._log = logging.getLogger("superdev.devops.scaling.policy")
        self.name = name
        self.metric = metric
        self._rules: list[dict[str, Any]] = []

    def add_rule(self, condition: str, threshold: float, action: str, amount: int) -> "ScalingPolicy":
        raise NotImplementedError

    def set_limits(self, min_replicas: int, max_replicas: int) -> "ScalingPolicy":
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self) -> list[str]:
        raise NotImplementedError
