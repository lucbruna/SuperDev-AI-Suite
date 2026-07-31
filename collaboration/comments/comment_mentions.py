"""Comment mentions extraction."""

from __future__ import annotations

import re

from collaboration.collaboration_protocols import extract_mentions

MENTION_PREFIX = "@"


def mentions_in(text: str, prefix: str = MENTION_PREFIX) -> list[str]:
    """Extracts @mentions from a comment body."""
    return extract_mentions(text, prefix)


def agent_mentions(text: str, agent_prefix: str = "agent:") -> list[str]:
    """Extracts agent mentions like @agent:planner."""
    pattern = re.compile(rf"{MENTION_PREFIX}{re.escape(agent_prefix)}(\w+)")
    return pattern.findall(text)
