from __future__ import annotations

import logging


class DjangoSupport:
    """Django framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.django")

    def detect(self, project_root: str) -> bool:
        import os
        return os.path.isfile(os.path.join(project_root, "manage.py"))

    def version(self) -> str:
        return "5.x"
