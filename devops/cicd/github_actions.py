from __future__ import annotations

import logging
from typing import Any


class GitHubActions:
    """GitHub Actions pipeline generator."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.github_actions")

    def generate(self, workflow: dict[str, Any]) -> str:
        raise NotImplementedError

    def validate(self, config: dict[str, Any]) -> list[str]:
        raise NotImplementedError
