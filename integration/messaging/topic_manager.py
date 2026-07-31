"""Topic management for messaging."""

from __future__ import annotations

import logging
from typing import Any


class TopicManager:
    """Creates and inspects message topics."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.messaging.topics")
        self._topics: dict[str, dict[str, Any]] = {}

    def create(self, topic: str, description: str = "") -> None:
        if topic in self._topics:
            raise ValueError(f"topic {topic!r} already exists")
        self._topics[topic] = {
            "topic": topic,
            "description": description,
            "messages": 0,
        }

    def has(self, topic: str) -> bool:
        return topic in self._topics

    def increment(self, topic: str) -> None:
        if topic in self._topics:
            self._topics[topic]["messages"] += 1

    def list(self) -> list[str]:
        return sorted(self._topics)

    def info(self, topic: str) -> dict[str, Any]:
        if topic not in self._topics:
            raise KeyError(topic)
        return self._topics[topic]

    def count_messages(self, topic: str) -> int:
        return self._topics.get(topic, {}).get("messages", 0)
