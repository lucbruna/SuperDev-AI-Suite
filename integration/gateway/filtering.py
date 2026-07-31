from __future__ import annotations

import logging
import re
from typing import Any


class RequestFilter:
    """Filters and validates incoming gateway requests."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.gateway.filtering")
        self._blocked_ips: set[str] = set()
        self._blocked_headers: dict[str, set[str]] = {}
        self._allowed_methods: set[str] = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
        self._path_patterns: list[re.Pattern] = []

    def block_ip(self, ip: str) -> None:
        self._blocked_ips.add(ip)

    def unblock_ip(self, ip: str) -> None:
        self._blocked_ips.discard(ip)

    def block_header_value(self, header: str, value: str) -> None:
        self._blocked_headers.setdefault(header.lower(), set()).add(value.lower())

    def allow_method(self, method: str) -> None:
        self._allowed_methods.add(method.upper())

    def deny_method(self, method: str) -> None:
        self._allowed_methods.discard(method.upper())

    def add_path_pattern(self, pattern: str) -> None:
        self._path_patterns.append(re.compile(pattern))

    def allow(self, method: str, path: str, headers: dict[str, str] | None = None,
              client_ip: str = "") -> bool:
        if method.upper() not in self._allowed_methods:
            return False
        if client_ip in self._blocked_ips:
            return False
        for pattern in self._path_patterns:
            if pattern.search(path):
                return False
        if headers:
            lowered = {k.lower(): v.lower() for k, v in headers.items()}
            for header, blocked in self._blocked_headers.items():
                if header in lowered and lowered[header] in blocked:
                    return False
        return True
