from __future__ import annotations

import logging
from typing import Any


class Firewall:
    """Manages firewall rules and security groups."""

    def __init__(self, name: str) -> None:
        self._log = logging.getLogger("superdev.devops.networking.firewall")
        self.name = name
        self._rules: list[dict[str, Any]] = []

    def allow(self, protocol: str, port: int | str, source: str = "0.0.0.0/0", **kwargs: Any) -> "Firewall":
        raise NotImplementedError

    def deny(self, protocol: str, port: int | str, source: str = "0.0.0.0/0", **kwargs: Any) -> "Firewall":
        raise NotImplementedError

    def remove_rule(self, rule_id: str) -> bool:
        raise NotImplementedError

    def rules(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def validate(self) -> list[str]:
        raise NotImplementedError
