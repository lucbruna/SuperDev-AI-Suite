from __future__ import annotations

import logging


class SpringSupport:
    """Spring framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.spring")

    def detect(self, project_root: str) -> bool:
        import os
        return os.path.isfile(os.path.join(project_root, "pom.xml")) or os.path.isfile(os.path.join(project_root, "build.gradle"))
