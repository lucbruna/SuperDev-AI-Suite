from __future__ import annotations

import logging


class FastAPISupport:
    """FastAPI framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.fastapi")

    def detect(self, project_root: str) -> bool:
        import os
        return os.path.isfile(os.path.join(project_root, "main.py"))
