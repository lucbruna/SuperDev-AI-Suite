from __future__ import annotations

import logging
from typing import Any


class NetworkPolicy:
    """Defines network isolation and segmentation policies."""

    def __init__(self, name: str) -> None:
        self._log = logging.getLogger("superdev.devops.networking.policy")
        self.name = name
        self._spec: dict[str, Any] = {}

    def allow_ingress(self, namespace: str, ports: list[int]) -> NetworkPolicy:
        raise NotImplementedError

    def allow_egress(self, namespace: str, ports: list[int]) -> NetworkPolicy:
        raise NotImplementedError

    def deny_all(self) -> NetworkPolicy:
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self) -> list[str]:
        raise NotImplementedError
