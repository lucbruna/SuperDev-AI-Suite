"""Agent publishing to marketplace."""
from __future__ import annotations

import time
import uuid
from typing import Any


class AgentPublisher:
    """Handles the publishing of agents to the marketplace."""

    def __init__(self) -> None:
        self._published: list[dict[str, Any]] = []

    def publish(self, agent_spec: dict[str, Any]) -> dict[str, Any]:
        agent_id = agent_spec.get("id", str(uuid.uuid4()))
        listing = {
            "agent_id": agent_id,
            "name": agent_spec.get("name", "Unnamed Agent"),
            "description": agent_spec.get("description", ""),
            "version": agent_spec.get("version", "1.0.0"),
            "author": agent_spec.get("author", "unknown"),
            "published_at": time.time(),
            "category": agent_spec.get("category", "general"),
            "tags": agent_spec.get("tags", []),
        }
        self._published.append(listing)
        return {"status": "published", "agent_id": agent_id}

    def unpublish(self, agent_id: str) -> bool:
        before = len(self._published)
        self._published = [p for p in self._published if p["agent_id"] != agent_id]
        return len(self._published) < before

    def get_published(self) -> list[dict[str, Any]]:
        return list(self._published)
