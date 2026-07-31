from __future__ import annotations

import logging


class NestSupport:
    """NestJS framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.nest")

    def detect(self, project_root: str) -> bool:
        import os
        pkg = os.path.join(project_root, "package.json")
        if not os.path.isfile(pkg):
            return False
        try:
            with open(pkg) as f:
                import json
                data = json.load(f)
            return "@nestjs/core" in data.get("dependencies", {})
        except Exception:
            return False
