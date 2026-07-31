from __future__ import annotations

import logging


class ReactSupport:
    """React framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.react")

    def detect(self, project_root: str) -> bool:
        import os
        return os.path.isfile(os.path.join(project_root, "package.json"))
