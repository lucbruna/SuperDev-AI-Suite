"""Port management."""

from __future__ import annotations

from enum import Enum
from typing import Any


class PortState(Enum):
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"


class PortRule:
    def __init__(self, port: int, state: PortState, service: str = "", description: str = "") -> None:
        self.port = port
        self.state = state
        self.service = service
        self.description = description


class PortManager:
    def __init__(self) -> None:
        self._rules: dict[int, PortRule] = {}
        self._scan_history: list[dict[str, Any]] = []
        self._default_state = PortState.CLOSED

    def add_rule(self, port: int, state: PortState, service: str = "", description: str = "") -> PortRule:
        rule = PortRule(port, state, service, description)
        self._rules[port] = rule
        return rule

    def remove_rule(self, port: int) -> bool:
        if port in self._rules:
            del self._rules[port]
            return True
        return False

    def get_state(self, port: int) -> PortState:
        rule = self._rules.get(port)
        return rule.state if rule else self._default_state

    def set_default(self, state: PortState) -> None:
        self._default_state = state

    def check_access(self, port: int) -> bool:
        return self.get_state(port) == PortState.OPEN

    def open_port(self, port: int, service: str = "") -> None:
        self._rules[port] = PortRule(port, PortState.OPEN, service)

    def close_port(self, port: int) -> None:
        self._rules[port] = PortRule(port, PortState.CLOSED)

    def list_open_ports(self) -> list[int]:
        return sorted([p for p, r in self._rules.items() if r.state == PortState.OPEN])

    def list_all_rules(self) -> list[dict[str, Any]]:
        return [
            {"port": r.port, "state": r.state.value, "service": r.service, "description": r.description}
            for r in sorted(self._rules.values(), key=lambda r: r.port)
        ]

    def scan_result(self, host: str, port: int, state: PortState) -> None:
        self._scan_history.append({"host": host, "port": port, "state": state.value})
