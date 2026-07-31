from __future__ import annotations

import logging
from typing import Any


class GitLabCI:
    """GitLab CI pipeline generator."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.gitlab_ci")

    def generate(self, workflow: dict[str, Any]) -> str:
        raise NotImplementedError

    def validate(self, config: dict[str, Any]) -> list[str]:
        raise NotImplementedError
