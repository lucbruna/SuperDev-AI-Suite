"""Security adapter — reuse the suite SSRF guards for URL validation.

Bridges to ``SuperDev.security.ssrf`` (CWE-918 protection). When the suite
module is unreachable, a compact stdlib fallback enforces the *same*
RFC 1918 / loopback / link-local policy, so studio pipelines stay safe even
without the platform.
"""
from __future__ import annotations

import ipaddress
import socket
from typing import Any
from urllib.parse import urlparse

from modules.ai_video_studio.suite_integration.adapters.base import (
    SuiteAdapter,
    ensure_suite_importable,
)

# Same policy as the suite guard: RFC 1918, loopback, link-local, CGNAT…
_BLOCKED_NETWORKS: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...] = (
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
)


class SecurityAdapter(SuiteAdapter):
    """SSRF URL validation through the suite security guards."""

    name = "security"
    description = "Reuse the suite SSRF guards (SuperDev.security.ssrf) for URL validation"
    platform_module = "SuperDev.security.ssrf"
    actions = ("validate_url", "is_internal_host")

    def validate_url(self, url: str, *, allow_private: bool = False) -> dict[str, Any]:
        """Return ``{safe: bool, reason?}`` — never raises."""
        ensure_suite_importable()
        try:
            from SuperDev.security.ssrf import validate_public_url

            validate_public_url(url, allow_private=allow_private)
            return {"safe": True, "url": url, "platform": True}
        except ImportError:
            return self._local_validate(url, allow_private=allow_private)
        except ValueError as e:
            return {"safe": False, "reason": str(e), "platform": self.available()}

    def is_internal_host(self, host: str) -> dict[str, Any]:
        """Return ``{internal: bool}`` — never raises."""
        ensure_suite_importable()
        try:
            from SuperDev.security.ssrf import is_internal_host as suite_check

            return {"internal": bool(suite_check(host)), "platform": True}
        except ImportError:
            return {"internal": self._local_is_internal(host), "platform": False}

    # ── Local fallback (same RFC 1918 policy, stdlib only) ──────
    @classmethod
    def _local_validate(cls, url: str, *, allow_private: bool = False) -> dict[str, Any]:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {"safe": False, "reason": f"scheme must be http/https, got {parsed.scheme!r}", "platform": False}
        host = parsed.hostname
        if not host:
            return {"safe": False, "reason": "url has no host", "platform": False}
        if not allow_private and cls._local_is_internal(host):
            return {"safe": False, "reason": f"url targets an internal/private address: {host!r}", "platform": False}
        return {"safe": True, "url": url, "platform": False}

    @staticmethod
    def _local_is_internal(host: str) -> bool:
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            try:
                addresses = [ipaddress.ip_address(info[4][0]) for info in socket.getaddrinfo(host, None)]
            except OSError:
                return False
            return any(any(a in net for net in _BLOCKED_NETWORKS) for a in addresses)
        return any(address in net for net in _BLOCKED_NETWORKS)
