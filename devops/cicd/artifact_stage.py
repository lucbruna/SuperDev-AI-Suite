from __future__ import annotations

import logging
from typing import Any


class ArtifactStage:
    """CI/CD artifact stage — stores and versions build outputs."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.artifact")

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def upload(self, artifact_path: str, name: str, version: str) -> dict[str, Any]:
        raise NotImplementedError

    def download(self, name: str, version: str, dest: str) -> str:
        raise NotImplementedError
