"""Integrations: deterministic dry-run clients for git, github, slack, CI."""
from __future__ import annotations

from modules.autonomous_developer.integrations.clients import (
    CIClient,
    GitClient,
    GitHubClient,
    IntegrationError,
    IntegrationResult,
    SlackNotifier,
)

__all__ = [
    "CIClient",
    "GitClient",
    "GitHubClient",
    "IntegrationError",
    "IntegrationResult",
    "SlackNotifier",
]
