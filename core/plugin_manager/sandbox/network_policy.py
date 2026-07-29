from __future__ import annotations

from urllib.parse import urlparse


class NetworkPolicy:
    def __init__(
        self,
        allowed_domains: list[str] | None = None,
        blocked_domains: list[str] | None = None,
        allowed_ports: list[int] | None = None,
    ) -> None:
        self.allowed_domains = allowed_domains or ["*"]
        self.blocked_domains = blocked_domains or []
        self.allowed_ports = allowed_ports or [80, 443, 8080]

    def check(self, url: str) -> None:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        for blocked in self.blocked_domains:
            if hostname == blocked or hostname.endswith("." + blocked):
                raise PermissionError(f"Domain '{hostname}' is blocked")

        if port not in self.allowed_ports:
            raise PermissionError(
                f"Port {port} is not allowed. Allowed ports: {self.allowed_ports}"
            )

        if "*" not in self.allowed_domains:
            allowed = False
            for domain in self.allowed_domains:
                if hostname == domain or hostname.endswith("." + domain):
                    allowed = True
                    break
            if not allowed:
                raise PermissionError(
                    f"Domain '{hostname}' is not in allowed domains: {self.allowed_domains}"
                )