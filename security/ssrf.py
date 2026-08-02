"""SSRF protection helpers (CWE-918, Server-Side Request Forgery).

Reusable guards for code paths that fetch URLs provided by users, agents or
external configuration. They refuse requests that would reach private,
loopback, link-local or reserved networks (RFC 1918, cloud metadata endpoints,
etc.) unless the caller explicitly opts in via ``allow_private=True``.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

_BLOCKED_NETWORKS: tuple[
    ipaddress.IPv4Network | ipaddress.IPv6Network, ...
] = (
    ipaddress.ip_network("0.0.0.0/8"),        # "this" network
    ipaddress.ip_network("10.0.0.0/8"),       # RFC 1918
    ipaddress.ip_network("100.64.0.0/10"),    # CGNAT
    ipaddress.ip_network("127.0.0.0/8"),      # loopback
    ipaddress.ip_network("169.254.0.0/16"),   # link-local / cloud metadata
    ipaddress.ip_network("172.16.0.0/12"),    # RFC 1918
    ipaddress.ip_network("192.0.0.0/24"),     # IETF protocol assignments
    ipaddress.ip_network("192.168.0.0/16"),   # RFC 1918
    ipaddress.ip_network("198.18.0.0/15"),    # benchmarking
    ipaddress.ip_network("198.51.100.0/24"),  # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),   # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),      # multicast
    ipaddress.ip_network("240.0.0.0/4"),      # reserved
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
    ipaddress.ip_network("::ffff:0:0/96"),    # IPv4-mapped IPv6
)

_ALLOWED_SCHEMES = frozenset({"http", "https"})


def _is_blocked(
    address: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> bool:
    return any(address in network for network in _BLOCKED_NETWORKS)


def _resolve_addresses(
    host: str,
) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """Resolve a hostname to IP addresses (best-effort, DNS rebinding caveat)."""
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return []
    addresses: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
    for info in infos:
        try:
            addresses.append(ipaddress.ip_address(info[4][0]))
        except ValueError:
            continue
    return addresses


def is_internal_host(host: str) -> bool:
    """True when *host* is, or resolves to, a private/internal address."""
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return any(_is_blocked(a) for a in _resolve_addresses(host))
    return _is_blocked(address)


def resolve_public_url(url: str, allow_private: bool = False) -> tuple[str, list[str]]:
    """Resolve *url* once and return (url, pinned_ip_set).

    Callers MUST connect to one of the returned pinned IPs (preserving the
    Host header) instead of re-resolving the hostname, which is the
    DNS-rebinding window.
    """
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError(
            f"URL scheme must be http or https, got {parsed.scheme!r}")
    host = parsed.hostname
    if not host:
        raise ValueError(f"URL has no host: {url!r}")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        # Hostname: resolve once and pin — the returned set is what callers
        # must connect to, closing the re-resolve/rebind window.
        addresses = _resolve_addresses(host)
        if not allow_private and any(_is_blocked(a) for a in addresses):
            raise ValueError(
                f"URL targets an internal/private address: {host!r}")
        return url, [a.compressed for a in addresses]
    if not allow_private and _is_blocked(address):
        raise ValueError(
            f"URL targets an internal/private address: {host!r}")
    return url, [str(address)]


def validate_public_url(url: str, allow_private: bool = False) -> str:
    """Validate *url* is an http(s) URL that does not target internal networks.

    Raises ``ValueError`` for unsupported schemes, missing hosts and hosts
    that resolve to private/loopback/link-local addresses, unless
    *allow_private* is explicitly set to True.

    Hostnames whose DNS resolution fails are allowed and will fail naturally
    at the HTTP layer (fail-open only on the allow side; internal targets are
    always rejected). DNS-rebinding is mitigated best-effort: the host is
    re-checked at validation time and blocking is conservative (any internal
    record blocks the request).
    """
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError(
            f"URL scheme must be http or https, got {parsed.scheme!r}")
    # Reject internal hosts at validation time (defense in depth);
    # connect-time pinning is provided by resolve_public_url().
    host = parsed.hostname
    if not host:
        raise ValueError(f"URL has no host: {url!r}")
    if not allow_private and is_internal_host(host):
        raise ValueError(
            f"URL targets an internal/private address: {host!r}")
    return url
