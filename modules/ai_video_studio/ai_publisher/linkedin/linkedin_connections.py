"""LinkedIn Connections — network growth and outreach (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class LinkedInConnections:
    """Track and guide connection growth on LinkedIn."""

    def __init__(self) -> None:
        self._network: list[dict] = []

    def add_connection(self, *, name: str = "", title: str = "", industry: str = "") -> dict:
        """Record a new connection."""
        connection = {"name": name or "Unknown", "title": title or "", "industry": industry or ""}
        self._network.append(connection)
        return connection

    def outreach_message(self, *, recipient_name: str = "", context: str = "") -> str:
        """Draft a personalized connection request."""
        base = f"Hi {recipient_name or 'there'}, I came across your profile"
        if context:
            return f"{base} while following {context}. I would like to connect and learn from your experience."
        return f"{base} and would like to connect."

    def network_summary(self) -> dict:
        by_industry: dict[str, int] = {}
        for conn in self._network:
            industry = conn["industry"] or "unknown"
            by_industry[industry] = by_industry.get(industry, 0) + 1
        return {"total": len(self._network), "by_industry": by_industry}

    def stats(self) -> dict[str, int]:
        return {"connections": len(self._network)}


_CONNECTIONS: LinkedInConnections | None = None


def get_linkedin_connections() -> LinkedInConnections:
    """Get the module-level singleton LinkedIn connections manager."""
    global _CONNECTIONS
    if _CONNECTIONS is None:
        _CONNECTIONS = LinkedInConnections()
    return _CONNECTIONS
